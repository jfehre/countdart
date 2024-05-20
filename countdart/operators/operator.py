""" Base Operator """
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, List

import numpy as np
import redis
from pydantic import TypeAdapter

from countdart.database.schemas.config import AllConfigModel
from countdart.utils.misc import encode_numpy

__all__ = "BaseOperator"


class BaseOperator(ABC):
    """The base class of operators.
    This class defines the minimal interface, which must be implemented by all
    operators.

    If redis_key is defined, a connection to redis is build and the result of
    the call function will be send to redis.
    """

    def __init__(self, redis_key: str = None, config: List[AllConfigModel] = None):
        if redis_key:
            self.r = redis.Redis(host="redis", port=6379)
            self.r_key = redis_key
        else:
            self.r = None
            self.r_key = None
        self.config = None
        if config:
            self.config = config
            # configure
            self.configure(self.config)

    @abstractmethod
    def call(self, *args, **kwargs):
        """The function which executes the logic of an operator"""

    def send_result_to_redis(self, data: Any):
        """Will send result of operator to redis, if redis_key
        was given on initialization. Else it will do nothing.

        Will append class name of operator to redis_key.

        """
        if self.r:
            # encode if data is numpy
            if isinstance(data, np.ndarray):
                data = encode_numpy(data)
            else:
                data = json.dumps(data)
            redis_result_key = f"{self.r_key}_{self.__class__.__name__}"
            self.r.set(redis_result_key, data)

    def receive_config_from_redis(self):
        """Check redis if config for this operator changed.

        It will append "_config" to redis key to look for configs. The config
        representation is a json dict.

        It will look for the operator class name as key in the config, and validate
        the given value as list of config models.
        The reason for this behavior is that multiple operators can share the same
        redis config path.
        After applying the changes, the config will be deleted from redis to avoid
        updating a second time.
        """
        if self.r:
            all_conf = self.r.get(f"{self.r_key}_config")
            if all_conf:
                all_conf = json.loads(all_conf)
                # check if config for this operator exists
                try:
                    op_conf = all_conf.pop(self.__class__.__name__)
                except KeyError:
                    return
                # convert and update config
                op_conf = [
                    TypeAdapter(AllConfigModel).validate_python(c) for c in op_conf
                ]
                if self.config != op_conf:
                    self.config = op_conf
                    self.configure(op_conf)
                # delete config, because it was processed
                self.r.set(f"{self.r_key}_config", json.dumps(all_conf))

    def __call__(self, *args, **kwargs):
        self.receive_config_from_redis()
        result = self.call(*args, **kwargs)
        self.send_result_to_redis(result)
        return result

    def teardown(self):
        """Function to clean up code,
        e.g closing of file handlers and connections"""
        if self.r is not None:
            self.r.close()

    def configure(self, configs=List[AllConfigModel]):
        """configure operator"""
        if configs is None:
            return
        for config in configs:
            if hasattr(self, "set_config"):
                self.set_config(config)
            else:
                logging.warning(
                    f"Operator {self.__class__.__name__} does"
                    + "not support configurations."
                )
