""" Calculate the tip of the dart """
import numpy as np

from countdart.operators.operator import BaseOperator
from countdart.utils.misc import BBox, Line

__all__ = "DartTipCalculator"


class DartTipCalculator(BaseOperator):
    """Calculates the exact point in image coordinates,
    where the dart is inside the board
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, image: np.ndarray, roi: BBox, line: Line):
        """Returns end of given line in image coordinates.
        This line is the end of the dart tip which is inside
        the dartboard.
        We assume it is always the first point of the given line.

        Args:
            image (np.ndarray): result image for shape
            roi (BBox): region of interest, in which the line lies.
            Given in percentage of the image
            line (Line): line given in percentage of the roi.

        Returns:
            _type_: _description_
        """

        img_h, img_w, _ = image.shape
        roi_x, roi_y, roi_w, roi_h = roi.to_pixel(img_w, img_h)
        # draw line
        # convert from percentage to pixel
        # draw line
        if line:
            # convert from percentage to pixel
            (
                _,
                _,
                lx2,
                ly2,
            ) = line.to_pixel(roi_w, roi_h)
            # return tip of the dart.
            # I currently assume it is always the first point of the line
            return (lx2 + roi_x, ly2 + roi_y)
        return None
