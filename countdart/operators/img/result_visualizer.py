"""This module contains a visualizer. This is mostly for debug purpose"""

import cv2
import numpy as np

from countdart.operators.img.bbox_detector import BBox
from countdart.operators.operator import BaseOperator


class ResultVisualizer(BaseOperator):
    """An operator to visualize all results in an image.
    Returns the visualized image
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(
        self, image: np.ndarray, bbox: BBox, label: str, line: np.ndarray
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

        Returns:
            np.ndarray: visualized image
        """
        img_h, img_w, _ = image.shape
        x, y, w, h = bbox.to_pixel(img_w, img_h)
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
        # draw line
        # convert from percentage to pixel
        if line.ndim > 0:
            lx1 = int((line[0] * w) + x)
            ly1 = int((line[1] * h) + y)
            lx2 = int((line[2] * w) + x)
            ly2 = int((line[3] * h) + y)
            vis_img = cv2.line(
                vis_img, (lx1, ly1), (lx2, ly2), color=(0, 0, 255), thickness=2
            )
        return vis_img
