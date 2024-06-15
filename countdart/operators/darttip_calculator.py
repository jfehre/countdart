""" Calculate the tip of the dart """
import numpy as np

from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import BBox, Line

__all__ = "DartTipCalculator"


@OPERATORS.register_class
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
        # convert from percentage to pixel
        roi_x, roi_y, roi_w, roi_h = roi.to_pixel(img_h, img_w)
        # draw line
        # draw line
        if line:
            # convert from percentage to pixel
            (
                lx1,
                ly1,
                lx2,
                ly2,
            ) = line.to_pixel(roi_h, roi_w)
            # return tip of the dart.
            # I currently assume the tip is always on the bottom of the image
            if ly1 < ly2:
                return (lx2 + roi_x, ly2 + roi_y)
            else:
                return (lx1 + roi_x, ly1 + roi_y)

        return None
