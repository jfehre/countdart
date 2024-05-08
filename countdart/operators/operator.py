""" Base Operator """
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping

import numpy as np
import redis

from countdart.utils.misc import encode_numpy

__all__ = "BaseOperator"

OperatorConfig = Mapping[str, str]


class BaseOperator(ABC):
    """The base class of operators.
    This class defines the minimal interface, which must be implemented by all
    operators.

    If redis_key is defined, a connection to redis is build and the result of
    the call function will be send to redis.
    """

    def __init__(self, redis_key: str = None, config: Dict[str, Any] = None):
        if redis_key:
            self.r = redis.Redis(host="redis", port=6379)
            self.r_key = redis_key
        else:
            self.r = None
            self.r_key = None
        self.config = None
        if config:
            self.config = config

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
            redis_result_key = f"{self.r_key}_{self.__class__.__name__}"
            self.r.set(redis_result_key, data)

    def receive_config_from_redis(self):
        """Check redis if config for this operator changed.

        It will append "_config" to redis key to look for configs. The config
        representation is a json dict.
        Afterwards it will look for the operator class name as key in the config,
        because multiple operators can share the same redis config path.
        """
        if self.r:
            all_conf = self.r.get(f"{self.r_key}_config")
            all_conf = json.loads(all_conf)
            # check if config for this operator exists
            try:
                op_conf = all_conf[self.__class__.__name__]
            except KeyError:
                return
            # update config
            if self.config != op_conf:
                self.config = op_conf
                self.configure(op_conf)

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

    def configure(self, config_model: OperatorConfig):
        """configure operator"""
        for key, value in config_model.items():
            if hasattr(self, "set_config"):
                self.set_config(key, value)
            else:
                logging.warning(
                    f"Operator {self.__class__.__name__} does"
                    + "not support configurations."
                )
