"""
Cam schema for the database.
"""
from typing import Optional

from pydantic import ConfigDict, Field

from .base import BaseModel, PyObjectId

__all__ = (
    "Cam",
    "CamBase",
    "CamCreate",
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


class Cam(CamBase):
    """Cam schema. This will also be saved in the mongo database as a collection."""

    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)


class CamCreate(CamBase):
    """Cam schema used to create new cam"""

    pass


class CamPatch(BaseModel):
    """Cam schema to patch a existing cam.
    Contains all fields which can be patched
    """

    card_name: Optional[str] = None
    active: Optional[bool] = None


class CamHardware(BaseModel):
    """Cam hardware schema.
    Represents a camera connected to the system.
    contains the current hardware id and the card name of the camera.
    """

    hardware_id: int
    card_name: str
