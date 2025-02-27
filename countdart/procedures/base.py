""" BaseProcedure to count darts. """

from abc import ABC, abstractmethod
from typing import Dict, List

from celery.contrib.abortable import AbortableTask

from countdart.database.schemas.config import AllConfigModel
from countdart.operators.operator import BaseOperator
from countdart.utils.registry import Registry

PROCEDURES = Registry("algorithms")


class BaseProcedure(AbortableTask, ABC):
    """Parent class for all algorithms, which process
    incoming images and detect thrown darts.
    These algorithms will be processed as celery task.
    So please register all children to celery.
    """

    def __init__(
        self,
        name: str = None,
        op_configs: Dict[str, List[AllConfigModel]] = None,
        **kwargs,
    ):
        """Set name to the class name. Is used by celery
        to reference the algorithm on runtime.

        Add unused kwargs to build procedure from registry,
        even if it contains more fields
        """
        self.op_configs = op_configs
        # use class name as name, otherwise celery will not find the task
        self.name = self.__name__

    @abstractmethod
    def run(self, *args, **kwargs):
        """Image processing happens here."""
        pass

    @abstractmethod
    def operators() -> List[BaseOperator]:
        """List all operator classes used in the run method"""
        pass

    def get_config(self):
        """return possible configs of this algorithm.
        These configs are not initialized with actual values.
        Furhtermore they depends heavily on the operators defined
        in the procedure
        """
        config_dict = {}
        for operator in self.operators:
            config_dict[operator.__name__] = operator.get_config(operator)
        return config_dict

    def __call__(self, *args, **kwargs):
        """will call run"""
        return self.run(*args, **kwargs)
