"""Schema of a dartboard setup. Each dartboard contains
a list of cameras and a state (active).
May also contain more settings in the future.
"""
from typing import List, Optional

from pydantic import ConfigDict, Field

from .base import BaseModel, PyObjectId

__all__ = (
    "Dartboard",
    "DartboardBase",
    "DartboardCreate",
    "DartboardPatch",
)


class DartboardBase(BaseModel):
    """
    Base schema for a configurable dartboard setup.
    """

    name: str
    active: bool = False


class Dartboard(DartboardBase):
    """Dartboard schema. This will also be saved in the database as a table."""

    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)
    cams: List[PyObjectId] = []
    active_celery_tasks: List[str] = []


class DartboardCreate(DartboardBase):
    """Dartboard schema used to create new dartboard"""

    pass


class DartboardPatch(BaseModel):
    """Dartboard schema to patch a dartboard.
    Contains all fields which can be patched
    """

    name: Optional[str] = None
    active: Optional[bool] = None
    cams: Optional[List[PyObjectId]] = None
    active_celery_tasks: Optional[List[str]] = None
