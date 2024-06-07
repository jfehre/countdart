""" This module contains a line detector """

import cv2
import numpy as np

from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import BBox, Line

__all__ = "HoughLineDetector"


@OPERATORS.register_class
class HoughLineDetector(BaseOperator):
    """The HoughLineDetector is used to detect straight lines
    in an image. This operator is based on opencv HoughLinesP function.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, image: np.ndarray, roi: BBox):
        """Receives an image and a region of interest as bounding box.
        The image is cropped to the bounding box and the hough lines
        are calculated. Afterwards this operator searches for the
        longest line found.

        It will return the longest line in percentages of the given region of
        interest.

        Args:
            image (np.ndarray): full image
            roi (BBox): region of interest in percentages of the full image

        Returns:
            _type_: the longest found hough line in percentages of the roi
        """
        img_h, img_w = image.shape
        # convert to pixel
        x, y, w, h = roi.to_pixel(img_w, img_h)
        roi = image[y : y + h, x : x + w]
        roi_h, roi_w = roi.shape
        # edge detector
        # canny = cv2.Canny(roi, 50, 200, None, 3)
        # hough line detector
        lines = cv2.HoughLinesP(roi, 1, np.pi / 45, 10, None, 70, 20)
        # select longest line
        new_line = None
        max_dist = 0
        if lines is not None:
            for i in range(0, len(lines)):
                line = lines[i][0]
                # calculate distance
                dist = np.linalg.norm(
                    np.array([line[0], line[1]]) - np.array([line[2], line[3]])
                )
                if dist > max_dist:
                    # convert to percentages
                    new_line = Line.from_pixel(line, roi_w, roi_h)
                    max_dist = dist
        return new_line
