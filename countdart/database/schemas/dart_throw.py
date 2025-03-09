"""
Schema for a single dart throw
"""

from typing import Tuple

from pydantic import ConfigDict, Field

from .base import BaseModel, PyObjectId

__all__ = (
    "DartThrow",
    "DartThrowBase",
)


class DartThrowBase(BaseModel):
    """
    Base schema for a dart throw.

    Attributes:
        score: str: The score of the dart throw
        confidence: float: The confidence of the score
        point: Tuple[float, float]: The point where the dart hit the board
    """

    score: str
    confidence: float
    point: Tuple[float, float]


class DartThrow(BaseModel):
    """
    Dart throw schema which is stored in the database as a collection

    Attributes:
        id: PyObjectId: The unique identifier of the dart throw
    """

    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)
