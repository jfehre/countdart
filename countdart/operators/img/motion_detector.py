"""Motion Detector Operator"""

from collections import deque
from typing import Any

import cv2
import logfire
import numpy as np

from countdart.database.schemas.config import FloatConfigModel, IntConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator
from countdart.utils.misc import encode_numpy

__all__ = "MotionDetector"


@OPERATORS.register_class
class MotionDetector(BaseOperator):
    """Motion Detector Operator.
    Will be used to detect motion in the images
    This operator will also resize the image if the resize parameter
    is less than 1.
    """

    resize = FloatConfigModel(
        name="resize",
        default_value=0.25,
        description="Factor to resize image",
        max_value=1,
        min_value=0,
    )

    threshold = IntConfigModel(
        name="threshold",
        default_value=50,
        description="Threshold for the motion detection. "
        "Lower thresholds may pick up more background noise.",
        max_value=255,
        min_value=0,
    )

    def __init__(self, **kwargs):
        self._last_image = None
        self.motion_buffer = deque(maxlen=5)  # Buffer to store the last 5 frames
        super().__init__(**kwargs)

    def send_result_to_redis(self, data: Any):
        """Overwrite base class to only send, if data is not None."""
        if self._r:
            # encode if data is numpy
            if not np.all(data == 0):
                data = encode_numpy(data)
                redis_result_key = f"{self._r_key}_{self.__class__.__name__}"
                self._r.set(redis_result_key, data)

    def call(self, image: np.array, **kwargs) -> np.array:
        """Add new frame to change detector and return trigger signal.
        Resizes the image.
        """
        # resize image with scaling factor
        with logfire.span("resize"):
            image = cv2.resize(image, None, fx=self.resize.value, fy=self.resize.value)

        if self._last_image is not None:
            # calculate diff
            with logfire.span("diff"):
                diff = cv2.absdiff(self._last_image, image)
            # to grayscale
            with logfire.span("grayscale"):
                diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            # Gaussian blur
            blur = cv2.GaussianBlur(diff, (3, 3), 0)
            # Threshold
            with logfire.span("threshold"):
                _, thresh = cv2.threshold(
                    blur, self.threshold.value, 255, cv2.THRESH_BINARY
                )

            self.motion_buffer.append(thresh)

            # Check if motion is consistent across all frames in the buffer
            if len(self.motion_buffer) == self.motion_buffer.maxlen:
                consistent_motion = np.all(
                    [np.any(frame) for frame in self.motion_buffer]
                )
                if consistent_motion:
                    with logfire.span("copy image"):
                        self._last_image = image
                    return np.array(thresh, dtype=np.uint8)
                else:
                    return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            else:
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        else:
            self._last_image = image
            return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    def reset(self, image: np.array) -> bool:
        """Reset the operator to initial state"""
        image = cv2.resize(image, None, fx=self.resize.value, fy=self.resize.value)
        self._last_image = image
        return True
