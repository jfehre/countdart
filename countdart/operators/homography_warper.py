"""Homography warper. Will warp a given image onto a dartboard model.
Needs to be initialized with calibration points to calculate
"""
from typing import List

import cv2
import numpy as np

from countdart.database.schemas import CalibrationPoint
from countdart.operators.operator import BaseOperator
from countdart.utils.dartboard_model import DartboardModel

__all__ = "HomographyWarper"


class HomographyWarper(BaseOperator):
    def __init__(
        self, calib_points: List[CalibrationPoint], img_shape: np.ndarray
    ) -> None:
        self.dartboard_model = DartboardModel()
        self.update_warp(calib_points, img_shape)

    def update_warp(
        self, calib_points: List[CalibrationPoint], img_shape: np.ndarray
    ) -> None:
        """Calculates warp matrix, based on calibration points and image shape.
        Output shape is based on the dartboard schemata.
        Saves the warp matrix in the class object

        Args:
            calib_points (CalibrationPoint): calibration points in percentage of
                        image shape
            img_shape (np.ndarray): input image shape
        """
        img_points = []
        obj_points = []
        for point in calib_points:
            # points are given in percentage, so get the real value based on img shape
            img_points.append((point.x * img_shape[0], point.y * img_shape[1]))
            # get corresponding obj point from dartboard model
            corr_dartboard_point = self.dartboard_model.get_outer_point(point.label)
            obj_points.append(corr_dartboard_point)
        self.img_points = np.array(img_points)
        self.obj_points = np.array(obj_points)
        # find homography from object points to image points
        h, _ = cv2.findHomography(self.obj_points, self.img_points)
        # find inverse, because we want to map points from image plane to object plane
        h_inv = np.linalg.inv(h)
        # translation matrix, because the world plane has negative points
        # and the top should be 20-1
        translate = self.dartboard_model.get_translation_vector()
        # combine homography with translation matrix
        self.warp_matrix = np.matmul(translate, h_inv)

    def call(self, image: np.array, **kwargs) -> np.array:
        """Gets input image and warps it onto a dartboard model

        Args:
            image (np.array): input image

        Returns:
            np.array: warped image
        """
        # warp image
        img_dst = cv2.warpPerspective(image, self.warp_matrix, (700, 700))
        # flip image (i dont know why...)
        img_dst = cv2.flip(img_dst, 0)
        return img_dst
