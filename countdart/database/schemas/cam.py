"""
Cam schema for the database.
"""
from typing import Optional

from sqlmodel import Field

from .base import BaseModel

__all__ = (
    "Cam",
    "CamBase",
    "CamCreate",
)


class CamBase(BaseModel):
    """
    Base schema for a configurable dartboard setup.
    """

    name: str
    active: bool


class Cam(CamBase, table=True):
    """Cam schema. This will also be saved in the database as a table."""

    id: Optional[int] = Field(default=None, primary_key=True)


class CamCreate(CamBase):
    """Cam schema used to create new cam"""

    pass


class CamRead(CamBase):
    """Cam schema which is returned from fastapi."""

    id: int


class CamPatch(BaseModel):
    """Cam schema to patch a existing cam.
    Contains all fields which can be patched
    """

    name: Optional[str] = Field(default=None)
    active: Optional[bool] = Field(default=None)
