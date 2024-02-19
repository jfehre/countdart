"""Schema of a dartboard setup. Each dartboard contains
a list of cameras and a state (active).
May also contain more settings in the future.
"""
from typing import Optional

from sqlmodel import Field

from .base import BaseModel

__all__ = (
    "Dartboard",
    "DartboardBase",
    "DartboardCreate",
    "DartboardRead",
    "DartboardPatch",
)


class DartboardBase(BaseModel):
    """
    Base schema for a configurable dartboard setup.
    """

    name: str = Field(sa_column_kwargs={"unique": True})
    active: bool


class Dartboard(DartboardBase, table=True):
    """Dartboard schema. This will also be saved in the database as a table."""

    id: Optional[int] = Field(default=None, primary_key=True)


class DartboardCreate(DartboardBase):
    """Dartboard schema used to create new dartboard"""

    pass


class DartboardRead(DartboardBase):
    """Dartboard schema which is return from fastapi.
    We can not return Dartboard directly, because of possible
    relationships which will not be resolved.
    """

    id: int


class DartboardPatch(BaseModel):
    """Dartboard schema to patch a dartboard.
    Contains all fields which can be patched
    """

    name: Optional[str]
    active: Optional[bool]
