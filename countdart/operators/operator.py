""" Base Operator """
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import redis

from countdart.utils.misc import encode_numpy

__all__ = "BaseOperator"


class BaseOperator(ABC):
    """The base class of operators.
    This class defines the minimal interface, which must be implemented by all
    operators.
    If redis_key is defined, a connection to redis is build and the result of
    the call function will be send to redis

    """

    def __init__(self, redis_key: str = None):
        if redis_key:
            self.r = redis.Redis(host="redis", port=6379)
            self.r_key = redis_key
        else:
            self.r = None
            self.r_key = None

    @abstractmethod
    def call(self, *args, **kwargs):
        """The function which executes the logic of an operator"""

    def send_to_redis(self, data: Any):
        """Will send result of operator to redis, if redis_key
        was given on initialization. Else it will do nothing."""
        if self.r:
            # encode if data is numpy
            if isinstance(data, np.ndarray):
                data = encode_numpy(data)
            self.r.set(self.r_key, data)

    def __call__(self, *args, **kwargs):
        result = self.call(*args, **kwargs)
        self.send_to_redis(result)
        return result

    def teardown(self):
        """Function to clean up code,
        e.g closing of file handlers and connections"""
        if self.r is not None:
            self.r.close()
