""" This module contains a line detector """

import cv2
import numpy as np

from countdart.database.schemas.config import FloatConfigModel, IntConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import BBox, Line

__all__ = "HoughLineDetector"


@OPERATORS.register_class
class HoughLineDetector(BaseOperator):
    """The HoughLineDetector is used to detect straight lines
    in an image. This operator is based on opencv HoughLinesP function.
    """

    rho = FloatConfigModel(
        name="rho",
        default_value=1,
        description="Distance resolution of the accumulator in pixels",
        max_value=500,
        min_value=0,
    )

    theta = FloatConfigModel(
        name="theta",
        default_value=45,
        description="Angle resolution of the accumulator in degree",
        max_value=360,
        min_value=0,
    )

    threshold = IntConfigModel(
        name="threshold",
        default_value=10,
        description="Accumulator threshold. Only those lines are"
        "returned that get enough votes (> threshold)",
        max_value=500,
        min_value=0,
    )

    min_line_length = FloatConfigModel(
        name="min_line_length",
        default_value=70,
        description="Minimum line length."
        "Line segments shorter than that are rejected",
        max_value=500,
        min_value=0,
    )

    max_line_gap = FloatConfigModel(
        name="max_line_gap",
        default_value=20,
        description="Maximum allowed gap between points"
        "on the same line to link them",
        max_value=500,
        min_value=0,
    )

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
        lines = cv2.HoughLinesP(
            roi,
            self.rho.value,
            np.pi / self.theta.value,
            self.threshold.value,
            None,
            self.min_line_length.value,
            self.max_line_gap.value,
        )
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
