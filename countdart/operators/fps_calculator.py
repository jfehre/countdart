""" Operator to calculate fps on each call"""
import time

from countdart.operators.operator import BaseOperator

__all__ = "FpsCalculator"


class FpsCalculator(BaseOperator):
    """This class will call current fps, based on the frequency it is called"""

    def __init__(self):
        super().__init__()
        self.prev_frame_time = 0
        self.fps = None
        # factor for new frame if higher the average will change faster
        self.k = 0.05

    def call(self, **kwargs):
        """Call when new frame was processed or received"""
        new_frame_time = time.time()
        if self.prev_frame_time == 0:
            self.prev_frame_time = new_frame_time
            return 0
        else:
            # calculate current frame fps
            frame_fps = 1 / (new_frame_time - self.prev_frame_time)
            if not self.fps:
                self.fps = frame_fps
            # Calculate fps with exponential smoothing
            mean = (frame_fps * self.k) + ((1 - self.k) * self.fps)
        self.prev_frame_time = new_frame_time
        self.fps = mean
        return mean
