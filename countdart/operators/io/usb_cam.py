"""Uniform wrapper for USB cameras. It is based on the v4l2py package"""

import io
import logging
from typing import Any, Dict, List

import cv2
import numpy as np
from PIL import Image
from v4l2py import Device, iter_video_capture_devices
from v4l2py.device import BufferType, ControlType

from countdart.database.schemas import IntConfigModel
from countdart.database.schemas.config import (
    AllConfigModel,
    BooleanConfigModel,
    SelectConfigModel,
)
from countdart.operators.io.frame_grabber import FRAME_GRABBERS, FrameGrabber

__all__ = ["USBCam"]


@FRAME_GRABBERS.register_class
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

        # convert to numpy array based on frame format
        format = frame.format.pixel_format.human_str()
        if format == "YUYV":
            raw = np.frombuffer(frame.data, dtype=np.uint8).reshape(
                (frame.height, frame.width, 2)
            )
            img = cv2.cvtColor(raw, cv2.COLOR_YUV2RGB_YUYV)
        elif format == "MJPG":
            raw = np.frombuffer(frame.data, dtype=np.uint8)
            bgr = cv2.imdecode(raw, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        else:
            img = Image.open(io.BytesIO(frame.data))
        return np.asarray(img)

    def get_config(self):
        """Get possible configs about cam. Will read configs directly from cam
        and not from the database. We assume that the changes in the database,
        are applied on the initalization of this camera via config parameter.
        """
        configs = []
        with self.cam:
            for control in self.cam.controls.values():
                value = control.value
                # Check type of control and create config models
                if control.type is ControlType.INTEGER:
                    conf = IntConfigModel(
                        name=control.config_name,
                        default_value=control.default,
                        max_value=control.maximum,
                        min_value=control.minimum,
                        value=value,
                    )
                elif control.type is ControlType.BOOLEAN:
                    conf = BooleanConfigModel(
                        name=control.config_name,
                        default_value=control.default,
                        value=value,
                    )
                elif control.type is ControlType.MENU:
                    conf = SelectConfigModel(
                        name=control.config_name,
                        default_value=control.data[control.default],
                        data=control.data.values(),
                        value=control.data[value],
                    )
                else:
                    raise TypeError(
                        f"No model schemata implemented for type {control.type}."
                    )
                configs.append(conf)

            # Add frame formats to config as a selection based config, which contains
            # height, width, fps, format
            data = []
            for frame_size in self.cam.info.frame_sizes:
                data.append(
                    f"{frame_size.height}, {frame_size.width}, "
                    f"{frame_size.max_fps}, {frame_size.pixel_format.human_str()}"
                )
            # load current format
            format = self.cam.get_format(BufferType.VIDEO_CAPTURE)
            fps = int(self.cam.get_fps(BufferType.VIDEO_CAPTURE))
            value = (
                f"{format.height}, {format.width}, {fps},"
                f" {format.pixel_format.human_str()}"
            )
            # append to config
            configs.append(
                SelectConfigModel(
                    name="formats",
                    data=data,
                    default_value=value,
                    value=value,
                )
            )

        return configs

    def set_config(self, config: AllConfigModel) -> None:
        """apply individual config model to camera"""
        with self.cam:
            # special case for formats config
            if config.name == "formats":
                # check for deletion, do not reset format on deletion.
                if config.type != "_delete_":
                    height, width, fps, format = config.value.split(", ")
                    # check if cam is running, because we can only
                    # update format if cam is not running
                    if self.frame_iterator:
                        self.stop()
                        self.cam.set_format(
                            BufferType.VIDEO_CAPTURE, int(width), int(height), format
                        )
                        self.cam.set_fps(BufferType.VIDEO_CAPTURE, int(fps))
                        self.start()
                    else:
                        self.cam.set_format(
                            BufferType.VIDEO_CAPTURE, int(width), int(height), format
                        )
                        self.cam.set_fps(BufferType.VIDEO_CAPTURE, int(fps))
            else:
                try:
                    ctrl = self.cam.controls[config.name]
                    # check for deletion
                    if config.type == "_delete_":
                        ctrl.set_to_default()
                    else:
                        # Special case for menu controls,
                        # because value is handled as string externally
                        if config.type == "select":
                            ctrl.value = list(ctrl.data.keys())[
                                list(ctrl.data.values()).index(config.value)
                            ]
                        else:
                            if ctrl.is_writeable:
                                ctrl.value = config.value
                except KeyError:
                    logging.warning(f"Control {config.name} does not exist")

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
            available_cams.append({"source": dev.index, "name": dev.info.card})

        return available_cams
