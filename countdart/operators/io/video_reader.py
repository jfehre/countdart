""" This module contains a video reader based on opencv capture """

import logging
import time

import cv2
import numpy as np

from countdart.database.schemas.config import AllConfigModel, BooleanConfigModel
from countdart.operators.io.frame_grabber import FRAME_GRABBERS, FrameGrabber


@FRAME_GRABBERS.register_class
class VideoReader(FrameGrabber):
    """Frame grabber to read video specified by a path.
    Currently the video needs to be located inside the server.
    When creating it via GUI you need to know where the video
    is saved.
    """

    def __init__(self, source: str, **kwargs):
        self._source: str = source
        self._loop = False
        self._capture = cv2.VideoCapture(self._source)
        self._fps = 15
        self._last_frame_time = time.time()
        if not self._capture.isOpened():
            raise FileNotFoundError(f"Could not open {self._source}.")
        super().__init__(**kwargs)

    @property
    def image_size(self):
        """Get image size"""
        w = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return w, h, 3

    def start(self):
        """Start camera. Does nothing because
        video is loaded on initialization
        """
        pass

    def stop(self):
        """Stop camera. Does nothing."""
        pass

    def get_frame(self) -> np.ndarray:
        """Return frame"""
        # limit capture to fps
        now = time.time()
        # wait till limit reached
        while (now - self._last_frame_time) < (1 / self._fps):
            now = time.time()
        self._last_frame_time = now
        # get frame
        ret, frame = self._capture.read()
        if not ret:
            # Check if video is over
            if self._capture.get(cv2.CAP_PROP_POS_FRAMES) == self._capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            ):
                if self._loop:
                    self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self._capture.read()
                else:
                    raise StopIteration("No more frames.")
            else:
                logging.warning("Failed to capture frame")

        return np.array(frame)

    def get_config(self):
        """Return all configs"""
        configs = []
        configs.append(
            BooleanConfigModel(
                name="_loop",
                type="bool",
                default_value=False,
                value=self._loop,
            )
        )
        return configs

    def set_config(self, config: AllConfigModel):
        """Set config."""
        setattr(self, config.name, config.value)
