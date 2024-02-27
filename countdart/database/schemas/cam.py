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
    "CamRead",
    "CamPatch",
    "CamHardware",
)


class CamBase(BaseModel):
    """
    Base schema for a configurable dartboard setup.
    """

    card_name: str
    active: bool
    hardware_id: int


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

    card_name: Optional[str] = Field(default=None)
    active: Optional[bool] = Field(default=None)


class CamHardware(BaseModel):
    """Cam hardware schema.
    Represents a camera connected to the system.
    contains the current hardware id and the card name of the camera.
    """

    hardware_id: int
    card_name: str
