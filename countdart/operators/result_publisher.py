""" Operator to publish results in redis"""

from countdart.database.schemas import DartThrowBase, ResultMessage
from countdart.operators.operator import OPERATORS, BaseOperator

__all__ = "ResultPublisher"


@OPERATORS.register_class
class ResultPublisher(BaseOperator):
    """This class will publish the result
    of dart and hand recognition as a dict."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self._r:
            self._r.delete(f"{self._r_key}_{self.__class__.__name__}")

    def send_result_to_redis(self, data: ResultMessage):
        """Overwrite send to redis, because we want a list
        to push and pop results for collector procedure

        Will send result if redis_key
        was given on initialization. Else it will do nothing.

        Will append class name of operator to redis_key.

        """
        if self._r:
            redis_result_key = f"{self._r_key}_{self.__class__.__name__}"
            self._r.set(redis_result_key, data.model_dump_json())
            # self._r.lpush(redis_result_key, data)

    def call(self, detection: str, data: DartThrowBase = None, **kwargs):
        """Call when new result was received"""
        message = ResultMessage(cls=detection, content=data)
        return message
