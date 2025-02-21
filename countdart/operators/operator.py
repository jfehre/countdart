""" Base Operator """
import json
from abc import ABC, abstractmethod
from typing import Any, List

import numpy as np
import redis
from pydantic import TypeAdapter

from countdart.database.schemas.config import AllConfigModel, ConfigBaseModel
from countdart.settings import settings
from countdart.utils.misc import encode_numpy
from countdart.utils.registry import Registry

__all__ = "BaseOperator"

OPERATORS = Registry("operators")


class BaseOperator(ABC):
    """The base class of operators.
    This class defines the minimal interface, which must be implemented by all
    operators.

    If redis_key is defined, a connection to redis is build and the result of
    the call function will be send to redis.
    """

    def __init__(self, redis_key: str = None, config: List[AllConfigModel] = None):
        if redis_key:
            self._r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
            self._r_key = redis_key
        else:
            self._r = None
            self._r_key = None
        # set changed config
        self.config = config
        if self.config:
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
        if self._r:
            # encode if data is numpy
            if isinstance(data, np.ndarray):
                data = encode_numpy(data)
            else:
                data = json.dumps(data)
            redis_result_key = f"{self._r_key}_{self.__class__.__name__}"
            self._r.set(redis_result_key, data)

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
        if self._r:
            all_conf = self._r.get(f"{self._r_key}_config")
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
                self._r.set(f"{self._r_key}_config", json.dumps(all_conf))

    def __call__(self, *args, **kwargs):
        self.receive_config_from_redis()
        result = self.call(*args, **kwargs)
        self.send_result_to_redis(result)
        return result

    def teardown(self):
        """Function to clean up code,
        e.g closing of file handlers and connections"""
        if self._r is not None:
            self._r.close()

    @classmethod
    def get_config(cls) -> List[AllConfigModel]:
        """Return all attributes of operator which are of
        type or subtype of AllConfigModel. These attributes
        can be set by user"""
        configs = []
        attributes = [
            a
            for a in dir(cls)
            if not a.startswith("_") and not callable(getattr(cls, a))
        ]
        for attr in attributes:
            attr = getattr(cls, attr)
            if isinstance(attr, ConfigBaseModel):
                configs.append(attr)
        return configs

    def set_config(self, config: AllConfigModel):
        """Default function to set config of operator.
        Set config as instance attribute with config name
        and value (if it exists) or default_value.

        Args:
            config (AllConfigModel): Given config
        """
        setattr(self, config.name, config)

    def configure(self, configs=List[AllConfigModel]):
        """configure operator"""
        if configs is None:
            return
        for config in configs:
            self.set_config(config)
