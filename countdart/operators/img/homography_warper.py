""" This file contains the operator and all belonging functions,
which help to warp the source image into the dartboard world
coordinates.
"""
from typing import List, Tuple

import cv2
import numpy as np

from countdart.database.schemas import CalibrationPoint
from countdart.database.schemas.config import BooleanConfigModel, IntConfigModel
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

    use_remap = BooleanConfigModel(
        name="use_remap",
        default_value=False,
        description="Use remap instead of warpPerspective. "
        "This will slow down startup time, but may speed up fps.",
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
        self._img_shape = img_shape
        self._calib_points = calib_points
        # This will initialize following variables:
        # self._h, self._h_inv, self._map_y, self._map_x
        # self._translate
        self.update_warp()

    @property
    def size(self):
        """Return size of resulting image"""
        return (self._dartboard_model.outer_double_ring + self.margin.value) * 2

    def _warp_point(
        self, matrix: np.ndarray, pt: Tuple[float, float]
    ) -> Tuple[float, float]:
        """Warp given point (x, y) with given homography matrix

        Args:
            matrix (np.ndarray): homography matrix used to warp point
            pt (Tuple[int, int]): point (x, y)

        Returns:
            Tuple[int, int]: warped point (x', y')
        """
        # https://stackoverflow.com/a/57400980
        px = (matrix[0][0] * pt[0] + matrix[0][1] * pt[1] + matrix[0][2]) / (
            (matrix[2][0] * pt[0] + matrix[2][1] * pt[1] + matrix[2][2])
        )
        py = (matrix[1][0] * pt[0] + matrix[1][1] * pt[1] + matrix[1][2]) / (
            (matrix[2][0] * pt[0] + matrix[2][1] * pt[1] + matrix[2][2])
        )
        return (px, py)

    def _update_maps(self, img_shape: np.array, matrix: np.array) -> None:
        """Calculates and updates the warp maps 'self._map_x' and 'self._map_y'
        for given image and homography matrix.
        This maps can be used in cv2.remap

        Args:
            image (np.array): image shape
            matrix (np.array): homography matrix

        Returns:
            np.array: _description_
        """
        # https://stackoverflow.com/a/57400980
        self._map_y = np.zeros((img_shape[0], img_shape[1]), dtype=np.float32)
        self._map_x = np.zeros((img_shape[0], img_shape[1]), dtype=np.float32)
        for y in range(img_shape[0]):
            for x in range(img_shape[1]):
                pt_warped = self._warp_point(matrix, (x, y))
                self._map_x[y, x] = int(pt_warped[0])
                self._map_y[y, x] = int(pt_warped[1])

    def update_warp(self) -> None:
        """Calculates warp homograpyh and a warp mapping,
        based on calibration points and image shape.
        The warp mapping also contains a translation (based on image size),
        avoiding a result image with negative coordinates.
        Output shape is based on the dartboard schemata.
        Saves the warp matrix in the class object

        Args:
            calib_points (CalibrationPoint): calibration points in percentage of
                        image shape
            img_shape (np.ndarray): input image shape
        """
        img_points = []
        obj_points = []
        for point in self._calib_points:
            # points are given in percentage, so get the real value based on img shape
            img_points.append(
                (point.x * self._img_shape[1], point.y * self._img_shape[0])
            )
            # get corresponding obj point from dartboard model
            corr_dartboard_point = self._dartboard_model.get_outer_point(point.label)
            obj_points.append(corr_dartboard_point)
        self._img_points = np.array(img_points)
        self._obj_points = np.array(obj_points)
        # find homography from object points to image points
        self._h, _ = cv2.findHomography(self._obj_points, self._img_points)
        # find inverse, because we want to map points from image plane to object plane
        self._h_inv = np.linalg.inv(self._h)
        if self.use_remap.value:
            # translation matrix, because the world plane has negative points
            # and the top should be 20-1
            translate_warp = np.array(
                [[1, 0, -self.size / 2], [0, 1, -self.size / 2], [0, 0, 1]]
            )
            warp_remap = np.matmul(self._h, translate_warp)
            self._update_maps(self._img_shape, warp_remap)
        # create homography for warping with cv2.warpPerspective
        translate_homography = np.array(
            [[1, 0, self.size / 2], [0, 1, self.size / 2], [0, 0, 1]]
        )
        self._warp_homography = np.matmul(translate_homography, self._h_inv)

    def _warp_with_remap(self, image: np.array) -> np.array:
        """Maps image with calculated remap from self.update_warp_map

        Args:
            image (np.array): image to warp

        Returns:
            np.array: warped image
        """
        if self._map_x is None:
            self.update_warp()
        warped_image = cv2.remap(image, self._map_x, self._map_y, cv2.INTER_NEAREST)
        # cut to output size
        cutted = warped_image[0 : self.size, 0 : self.size]
        return cutted

    def _warp_with_homography(self, image: np.array) -> np.array:
        """Warps image with calculated homography and translation
        from self.update_warp_map.
        Same functionality than remap image but propably slower

        Args:
            image (np.array): image to warp

        Returns:
            np.array: warped image
        """
        # warp image
        return cv2.warpPerspective(
            image,
            self._warp_homography,
            (self.size, self.size),
            flags=cv2.INTER_NEAREST,
        )

    def call(self, image: np.array, **kwargs) -> np.array:
        """Gets input image and warps it onto a dartboard model and
        translate the image to non-negative
        Will also add a translation so the image is not negative.

        Args:
            image (np.array): input image

        Returns:
            np.array: warped image
        """
        if image.shape != self._img_shape:
            self._img_shape = image.shape
            self.update_warp()
        # warp image
        if self.use_remap.value:
            warped = self._warp_with_remap(image)
        else:
            warped = self._warp_with_homography(image)
        # flip image because origin is on top left and not bottom left
        return cv2.flip(warped, 0)

    def warp_point_to_model(self, x: float, y: float) -> Tuple[float, float]:
        """Warps single point to dartboard model. Will not add translation.

        Args:
            x (float): x
            y (float): y

        Returns:
            Tuple[int, int]: point in dartboard world coordinate
        """
        p = (x, y)
        return self._warp_point(self._h_inv, p)
