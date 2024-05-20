"""Change Detector Operator"""
import cv2
import numpy as np

from countdart.operators.operator import BaseOperator

__all__ = "ChangeDetector"


class ChangeDetector(BaseOperator):
    """Change detecter based on opencv Background Foreground Subtractor.
    Will be used to detect hand motion and darts on an empty board.
    This operator will also resize the image if the resize parameter
    is less than 1.
    """

    def __init__(self, resize: float = 0.5, **kwargs):
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
        self.resize = resize
        super().__init__(**kwargs)

    def call(self, image: np.array, learning_rate=-1, **kwargs) -> np.array:
        """Add new frame to change detector and return mask.
        Resizes the image.
        """
        # resize image with scaling factor
        image = cv2.resize(image, None, fx=self.resize, fy=self.resize)
        mask = self.fgbg.apply(image, learningRate=learning_rate)
        return mask
