""" Base Operator """
from abc import ABC, abstractmethod

__all__ = "BaseOperator"


class BaseOperator(ABC):
    """The base class of operators.
    This class defines the minimal interface, which must be implemented by all
    operators.
    Can also be used in the future to add hooks to the calls.

    """

    @abstractmethod
    def call(self, *args, **kwargs):
        """The function which executes the logic of an operator"""

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)
