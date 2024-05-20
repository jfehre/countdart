""" Calculates score """
import numpy as np

from countdart.operators.operator import BaseOperator
from countdart.utils.dartboard_model import DartboardModel

__all__ = "ScoreCalculator"


class ScoreCalculator(BaseOperator):
    """Calculates score with the help of the dartboard model"""

    def __init__(self, dartboard_model: DartboardModel, **kwargs):
        self._dartboard_model = dartboard_model
        super().__init__(**kwargs)

    def call(self, point_2d: np.ndarray):
        """Given a point in dartboard world coordinate system,
        returns score as a Tuple with string representation
        and actual score

        Args:
            point_2d (np.ndarray): point in dartboard world coordinate system

        Returns:
            _type_: calculated score
        """
        return self._dartboard_model.get_score(point_2d)
