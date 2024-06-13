"""Change Detector Operator"""

import cv2
import numpy as np

from countdart.database.schemas.config import FloatConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator

__all__ = "ChangeDetector"


@OPERATORS.register_class
class ChangeDetector(BaseOperator):
    """Change detecter based on opencv Background Foreground Subtractor.
    Will be used to detect hand motion and darts on an empty board.
    This operator will also resize the image if the resize parameter
    is less than 1.
    """

    resize = FloatConfigModel(
        name="resize",
        default_value=1,
        description="Factor to resize image",
        max_value=1,
        min_value=0,
    )

    def __init__(self, **kwargs):
        self._fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
        super().__init__(**kwargs)

    def call(self, image: np.array, learning_rate=-1, **kwargs) -> np.array:
        """Add new frame to change detector and return mask.
        Resizes the image.
        """
        # resize image with scaling factor
        image = cv2.resize(image, None, fx=self.resize.value, fy=self.resize.value)
        mask = self._fgbg.apply(image, learningRate=learning_rate)
        return mask
