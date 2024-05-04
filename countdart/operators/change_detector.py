"""Change Detector Operator"""
import cv2
import numpy as np

from countdart.operators import BaseOperator

__all__ = "ChangeDetector"


class ChangeDetector(BaseOperator):
    """Change detecter based on opencv Background Foreground Subtractor.
    Will be used to detect hand motion and darts on an empty board"""

    def __init__(self):
        super().__init__()
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

    def call(self, image: np.array, **kwargs):
        """Add new frame to change detector and return mask"""
        mask = self.fgbg.apply(image)
        return mask
