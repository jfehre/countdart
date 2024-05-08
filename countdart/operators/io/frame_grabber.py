"""This module contains the base class of frame grabbers"""

from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from countdart.operators.operator import BaseOperator

__all__ = ["FrameGrabber"]


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
