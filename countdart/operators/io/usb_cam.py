"""Uniform wrapper for USB cameras. It is based on the v4l2py package"""

import io
import logging
from typing import Any, Dict, List

import numpy as np
from PIL import Image
from v4l2py import Device, iter_video_capture_devices
from v4l2py.device import BufferType

from countdart.operators.io.frame_grabber import FrameGrabber

__all__ = ["USBCam"]


class USBCam(FrameGrabber):
    """Implementation of an usb cam with v4l2py"""

    def __init__(self, device_id: int, **kwargs) -> None:
        self.cam = Device.from_id(device_id)
        # Load self.cam.info
        self.cam.open()
        self.cam.close()
        self.frame_iterator = None
        super().__init__(**kwargs)

    @property
    def image_size(self):
        """Get image size"""
        format = self.cam.get_format(BufferType.VIDEO_CAPTURE)
        return format.width, format.height, 3

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

        # TODO: convert to numpy array
        img = Image.open(io.BytesIO(frame.data))
        return np.asarray(img)

    def set_config(self, key: str, value: Any) -> None:
        """set camera config by key and value"""
        if key == "reset" and value:
            self.reset_config()
        try:
            ctrl = self.cam.controls[key]
            ctrl.value = value
        except KeyError:
            logging.warning(f"Control {key} does not exist")

    def reset_config(self):
        """reset all camera configs"""
        self.cam.controls.set_to_default()
        self.config_raw = None

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
