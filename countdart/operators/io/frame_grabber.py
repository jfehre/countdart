"""This module contains the base class of frame grabbers"""

from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

import countdart.operators.io as io
from countdart.database.schemas.cam import Cam
from countdart.operators.operator import BaseOperator
from countdart.utils.registry import Registry

__all__ = ["FrameGrabber"]

FRAME_GRABBERS = Registry("frame_grabbers")


class FrameGrabber(BaseOperator, ABC):
    """Base class for frame grabbers.

    Describes the common interfaces for all frame grabbers
    """

    @property
    @abstractmethod
    def image_size(self) -> Tuple[int, int, int]:
        """The image size as tuple of (height, width, channels)"""

    @abstractmethod
    def start():
        """Starting the camera stream"""

    @abstractmethod
    def stop():
        """Stopping the camera stream"""

    @abstractmethod
    def get_frame() -> np.ndarray:
        """Return frame"""

    def call(self) -> np.ndarray:
        """Proxies the get_frame method"""
        return self.get_frame()

    def teardown(self):
        """calls framegrabber stop function and super()
        to clean up code and connections
        """
        self.stop()
        super().teardown()

    @classmethod
    def build_from_model(cls, model: Cam, **kwargs):
        """Build a framegraber from database model.
        Will check for model.type and create a framegraber from
        the countdart.operators.io module with the same name as
        given type.
        """
        c = getattr(io, model.type)
        return c(model.source, **kwargs)
