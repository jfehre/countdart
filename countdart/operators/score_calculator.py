""" Calculates score """
from typing import Tuple

import numpy as np

from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.dartboard_model import DartboardModel

__all__ = "ScoreCalculator"


@OPERATORS.register_class
class ScoreCalculator(BaseOperator):
    """Calculates score with the help of the dartboard model.
    Will also calculate a confidence, based on distance of the point
    """

    def __init__(self, dartboard_model: DartboardModel, **kwargs):
        self._dartboard_model = dartboard_model
        super().__init__(**kwargs)

    def call(self, point_2d: Tuple[float, float], point_2d_conf: Tuple[float, float]):
        """Given a point in dartboard world coordinate system,
        returns score as a Tuple with string representation
        and actual score.

        The point_2d_conf is used to calculate a confidence of the score.
        point_2d_conf should be the warped point_2d but with an offset of 1
        in x and y axis. The resulting distance between point_2d and
        point_2d_conf is a good indicator for the confidence

        Args:
            point_2d (Tuple[float, float]): point in dartboard world coordinate system
            point_2d_conf (Tuple[float, float]): point with offset 1 in
            dartboard world coordinate system

        Returns:
            _type_: calculated score
        """
        conf = np.linalg.norm(np.array(point_2d) - np.array(point_2d_conf))
        score_str, score = self._dartboard_model.get_score(point_2d)
        return score_str, 1 / max(conf, 1)
