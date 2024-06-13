""" This file contains the operator and all belonging functions,
which help to warp the source image into the dartboard world
coordinates.
"""
from typing import List, Tuple

import cv2
import numpy as np

from countdart.database.schemas import CalibrationPoint
from countdart.database.schemas.config import IntConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.dartboard_model import DartboardModel

__all__ = "HomographyWarper"


@OPERATORS.register_class
class HomographyWarper(BaseOperator):
    """Homography warper. Will warp a given image onto a dartboard model.
    Needs to be initialized with calibration points to calculate
    """

    margin = IntConfigModel(
        name="margin",
        default_value=55,
        description="Margin to add around warped dartboard",
        max_value=200,
        min_value=0,
    )

    def __init__(
        self,
        calib_points: List[CalibrationPoint],
        img_shape: np.ndarray,
        dartboard_model: DartboardModel = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._dartboard_model = dartboard_model
        if self._dartboard_model is None:
            self._dartboard_model = DartboardModel()
        self.update_warp(calib_points, img_shape)

    @property
    def size(self):
        """Return size of resulting image"""
        return (self._dartboard_model.outer_double_ring + self.margin.value) * 2

    def update_warp(
        self, calib_points: List[CalibrationPoint], img_shape: np.ndarray
    ) -> None:
        """Calculates warp matrix, based on calibration points and image shape.
        Also calculates a translation matrix, avoiding a result image with
        negative coordinates.
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
            corr_dartboard_point = self._dartboard_model.get_outer_point(point.label)
            obj_points.append(corr_dartboard_point)
        self._img_points = np.array(img_points)
        self._obj_points = np.array(obj_points)
        # find homography from object points to image points
        h, _ = cv2.findHomography(self._obj_points, self._img_points)
        # find inverse, because we want to map points from image plane to object plane
        self._h_inv = np.linalg.inv(h)
        # translation matrix, because the world plane has negative points
        # and the top should be 20-1
        self._translate = np.array(
            [[1, 0, self.size / 2], [0, 1, self.size / 2], [0, 0, 1]]
        )
        # combine homography with translation matrix
        self._combined_warp = np.matmul(self._translate, self._h_inv)

    def call(self, image: np.array, **kwargs) -> np.array:
        """Gets input image and warps it onto a dartboard model and
        translate the image to non-negative
        Will also add a translation so the image is not negative.

        Args:
            image (np.array): input image

        Returns:
            np.array: warped image
        """
        # warp image
        img_dst = cv2.warpPerspective(
            image,
            self._combined_warp,
            (self.size, self.size),
            flags=cv2.INTER_NEAREST,
        )
        # flip image (i dont know why...)
        img_dst = cv2.flip(img_dst, 0)
        return img_dst

    def warp_point_to_model(self, x: float, y: float) -> Tuple[int, int]:
        """Warps single point to dartboard model. Will not add translation.

        Args:
            x (float): x
            y (float): y

        Returns:
            Tuple[int, int]: point in dartboard world coordinate
        """
        p = (x, y)
        matrix = self._h_inv
        # https://stackoverflow.com/a/57400980
        px = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / (
            (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])
        )
        py = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / (
            (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])
        )

        return (int(px), int(py))
