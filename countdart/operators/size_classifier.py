""" This module contains a size classifier """
from typing import Dict, Tuple

from countdart.operators.operator import BaseOperator

__all__ = "DartTipCalculator"


class SizeClassifier(BaseOperator):
    """This class will classify a single float number,
    based on the given classes in the initialization.

    The classes are represented as a dict with the class label as key,
    and the (min, max) threshold as value.
    To classify a given number, it looks through all given classes and returns
    the label if the number is between min, max.
    If no class was found it returns "none".
    """

    def __init__(
        self,
        classes: Dict[str, Tuple[float, float]] = {
            "dart": (0.005, 0.1),
            "hand": (0.3, 0.6),
        },
        **kwargs,
    ):
        self.classes = classes
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
        for label, c in self.classes.items():
            if c[0] <= size <= c[1]:
                return label
        return "none"
