"""This module contains a visualizer. This is mostly for debug purpose"""

from typing import Tuple

import cv2
import numpy as np

from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import BBox, Line

__all__ = "ResultVisualizer"


@OPERATORS.register_class
class ResultVisualizer(BaseOperator):
    """An operator to visualize all results in an image.
    Returns the visualized image
    """

    def call(
        self,
        image: np.ndarray,
        bbox: BBox,
        label: str,
        line: Line,
        score: str,
        conf: float,
        img_tip: Tuple[int, int],
    ) -> np.ndarray:
        """Visualize results in one image.
        Draws the bounding box on the given image, adds a label and finally
        draws the found hough line into the original image.

        Returns the visualized image

        Args:
            image (np.ndarray): full image
            bbox (BBox): found bounding box in percentage
            label (str): classified label of bounding box
            line (np.ndarray): found hough line in percentage of bbox
            score (str): calculated dart score
            conf (float): confidence of calculated score
            img_tip(Tuple): Point2D of dart tip

        Returns:
            np.ndarray: visualized image
        """
        img_h, img_w, _ = image.shape
        x, y, w, h = bbox.to_pixel(img_h, img_w)
        vis_img = image.copy()
        # draw bbox on image
        vis_img = cv2.rectangle(
            vis_img, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2
        )
        # draw label
        vis_img = cv2.putText(
            vis_img,
            label,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=2,
            color=(255, 0, 0),
            thickness=2,
        )
        # draw score
        vis_img = cv2.putText(
            vis_img,
            f"{score}, {round(conf,1)}",
            (0, img_h),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=2,
            color=(255, 0, 0),
            thickness=4,
        )

        # draw line
        if line:
            # convert from percentage to pixel
            lx1, ly1, lx2, ly2 = line.to_pixel(h, w)
            # draw line with offset of bounding box
            vis_img = cv2.line(
                vis_img,
                (lx1 + x, ly1 + y),
                (lx2 + x, ly2 + y),
                color=(0, 0, 255),
                thickness=2,
            )

        # draw point
        if img_tip:
            vis_img = cv2.circle(vis_img, img_tip, 2, color=(0, 255, 0), thickness=-1)
        return vis_img
