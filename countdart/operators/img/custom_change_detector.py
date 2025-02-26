"""Change Detector Operator"""

import cv2
import logfire
import numpy as np

from countdart.database.schemas.config import FloatConfigModel, IntConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator

__all__ = "CustomChangeDetector"


@OPERATORS.register_class
class CustomChangeDetector(BaseOperator):
    """Custom Change Detector Operator.
    Will be used to detect changes in the images
    This operator will also resize the image if the resize parameter
    is less than 1.
    """

    resize = FloatConfigModel(
        name="resize",
        default_value=1,
        description="Factor to resize image",
        max_value=1,
        min_value=0,
    )

    high_thresh = IntConfigModel(
        name="high_thresh",
        default_value=100,
        description="High threshold for the change detection",
        max_value=255,
        min_value=0,
    )

    low_thresh = IntConfigModel(
        name="low_thresh",
        default_value=50,
        description="Low threshold for the change detection",
        max_value=255,
        min_value=0,
    )

    def __init__(self, **kwargs):
        self._last_image = None
        self.k = 0.05
        super().__init__(**kwargs)

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
            blur = cv2.GaussianBlur(diff, (5, 5), 0)
            # Threshold
            with logfire.span("threshold"):
                high_mask = blur >= self.high_thresh.value
                low_mask = (blur >= self.low_thresh.value) & (
                    blur < self.high_thresh.value
                )
                num_labels, labels = cv2.connectedComponents(high_mask.astype(np.uint8))
                thresh = np.zeros_like(blur, dtype=np.uint8)
                for label in range(1, num_labels + 1):
                    component_mask = labels == label
                    if np.any(component_mask & high_mask):
                        thresh[component_mask | low_mask] = 255
            # Calculate last image with exponential smoothing
            with logfire.span("copy image"):
                self._last_image = image
            return np.array(thresh, dtype=np.uint8)
        else:
            self._last_image = image
            return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    def reset(self, image: np.array) -> bool:
        """Reset the operator to initial state"""
        image = cv2.resize(image, None, fx=self.resize.value, fy=self.resize.value)
        self._last_image = image
        return True
