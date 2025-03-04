""" This module contains a size classifier """

from collections import deque

from countdart.database.schemas.config import FloatConfigModel
from countdart.operators.operator import OPERATORS, BaseOperator

__all__ = "DartTipCalculator"


@OPERATORS.register_class
class SizeClassifier(BaseOperator):
    """This class will classify a single float number,
    based on the given classes in the initialization.

    The classes are represented as a dict with the class label as key,
    and the (min, max) threshold as value.
    To classify a given number, it looks through all given classes and returns
    the label if the number is between min, max.
    If no class was found it returns "none".
    """

    dart_min = FloatConfigModel(
        name="dart_min",
        default_value=0.005,
        description="minimum of hand classifier",
        min_value=0,
        max_value=1,
    )

    dart_max = FloatConfigModel(
        name="dart_max",
        default_value=0.1,
        description="maximum of hand classifier",
        min_value=0,
        max_value=1,
    )

    hand_min = FloatConfigModel(
        name="hand_min",
        default_value=0.3,
        description="minimum of hand classifier",
        min_value=0,
        max_value=1,
    )

    hand_max = FloatConfigModel(
        name="hand_max",
        default_value=1,
        description="maximum of hand classifier",
        min_value=0,
        max_value=1,
    )

    def __init__(self, **kwargs):
        self.classification_buffer = deque(
            maxlen=15
        )  # Buffer to store the last 15 classifications
        super().__init__(**kwargs)

    def call(self, size: float) -> str:
        """Check if a class for given size exists.
        Returns the label of the class or "none" if no class
        exists, where the input number lies in between

        Args:
            size (float): number to classify

        Returns:
            str: label of the found classification. "none" if no
            class was found
        """

        if self.hand_min.value <= size <= self.hand_max.value:
            classification = "hand"
        elif self.dart_min.value <= size <= self.dart_max.value and all(
            c != "hand" for c in self.classification_buffer
        ):
            classification = "dart"
        else:
            classification = "none"

        # Update the classification buffer
        self.classification_buffer.append(classification)

        return classification
