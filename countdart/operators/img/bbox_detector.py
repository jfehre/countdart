""" This modules contains a bounding box detector """

from typing import Tuple

import cv2
import numpy as np

from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import BBox

__all__ = "BBoxDetector"


@OPERATORS.register_class
class BBoxDetector(BaseOperator):
    """Detects a bounding box in a binary image.
    The bounding box is returned as percentages of the given image
    in the format (x, y, w, h).
    As a second return value, the size of the bounding box in the given
    image is given as a ratio of the bounding box area to the given image.
    """

    def __init__(self, **kwargs):
        super().__init__()

    def call(self, image: np.ndarray) -> Tuple[BBox, float]:
        """Detects the bounding box in the given mask. The bounding box
        is calculated around all nonzero values in the given image,
        it does not matter if these values are connected or not.

        It returns the bounding box as (x, y, w, h). These values
        are no absolute pixel values, but represented as percentages
        of the given mask. This allows an easy usage on scaled images.
        As a second return value, the size of the bounding box area in
        respect to the given image is calculated (also in percentage).

        Args:
            image (np.ndarray): binary mask image

        Returns:
            Tuple[BBox, float]: (BBox, bbox_size)
        """
        img_h, img_w = image.shape
        # bounding box
        bbox = cv2.boundingRect(image)
        # scale bbox to percentage of image
        bbox_percentage = BBox.from_pixel(bbox, img_w, img_h)
        # count nonzero percentage
        bbox_ratio = (bbox[2] * bbox[3]) / (img_w * img_h)
        return bbox_percentage, bbox_ratio
