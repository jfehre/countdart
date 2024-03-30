"""Uniform wrapper for USB cameras. It is based on the v4l2py package"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import numpy as np
from v4l2py import Device, iter_video_capture_devices

__all__ = ["BaseCam", "USBCam"]


class BaseCam(ABC):
    """abstract base class which describes
    the interface with camera classes
    """

    @abstractmethod
    def start():
        """Starting the camera stream"""

    @abstractmethod
    def stop():
        """Stopping the camera stream"""

    @abstractmethod
    def get_frame() -> np.ndarray:
        """Return frame"""


class USBCam(BaseCam):
    """Implementation of an usb cam with v4l2py

    Args:
        BaseCam ():
    """

    def __init__(self, device_id: int, **kwargs) -> None:
        self.cam = Device.from_id(device_id, **kwargs)
        # Load self.cam.info (not used currently)
        self.cam.open()
        self.cam.close()
        self.frame_iterator = None
        super().__init__()

    def start(self):
        """Starting the camera stream"""
        self.cam.__enter__()
        self.frame_iterator = self.cam.__iter__()

    def stop(self):
        """Stopping the camera stream"""
        self.frame_iterator = None
        self.cam.__exit__()

    def get_frame(self) -> np.ndarray:
        """Return frame"""
        frame = next(self.frame_iterator)

        return frame.array

    @classmethod
    def get_available_cams(cls) -> List[Dict[str, Any]]:
        """Get available USB cameras. Use v4l2py iter_video_capture_devices
        to get available cameras. Will open and close each camera to check if
        it is available and to get camera information.
        Will return a list of available cameras.
        Each camera is represented as a dict like schemas.CamHardware.

        Returns:
            List[int]: List of available cameras represented as dict,
            representing schemas.CamHardware
        """
        available_cams = []
        for dev in iter_video_capture_devices():
            dev.open()
            dev.close()
            available_cams.append(
                {"hardware_id": dev.index, "card_name": dev.info.card}
            )

        return available_cams
