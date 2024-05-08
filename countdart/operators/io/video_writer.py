"""Module for video writers"""
import cv2
import numpy as np

from countdart.operators.operator import BaseOperator

__all__ = ["VideoWriter"]


class VideoWriter(BaseOperator):
    """OpenCV video writer.

    Writes frames to the given path
    """

    def __init__(self, path: str):
        self._path = path
        self._video_writer = None
        self._fourcc = cv2.VideoWriter.fourcc(*"MJPG")
        self._fps = 20
        super().__init__()

    def call(self, frame: np.ndarray):
        """Writes the frame to video file.
        Creates new video writer if it doesn't exist"""
        if self._video_writer is None:
            frame_shape = tuple(reversed(frame.shape[:2]))
            is_color = len(frame.shape) == 3 and frame.shape[2] == 3
            self._video_writer = cv2.VideoWriter(
                self._path, self._fourcc, self._fps, frame_shape, isColor=is_color
            )
            if not self._video_writer.isOpened():
                raise OSError(f"Could not open {self._path=}.")
        self._video_writer.write(frame)

    def teardown(self):
        """Closes videostream"""
        if self._video_writer is not None:
            self._video_writer.release()
            self._video_writer = None
        super().teardown()
