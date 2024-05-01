"""
Cam schema for the database.
"""
from typing import List, Optional, Union

from pydantic import ConfigDict, Field

from .base import BaseModel, PyObjectId

__all__ = (
    "CalibrationPoint",
    "Cam",
    "CamBase",
    "CamCreate",
    "CamPatch",
    "CamHardware",
)


class CalibrationPoint(BaseModel):
    """Defines calibration point. Should be a value between 0 and 1.
    Each calibration point describes a 2D point in percentage of the camera input image.
    This is used to calibrate camera images with an homography operator.
    """

    x: float = Field(None, ge=0, le=1)
    y: float = Field(None, ge=0, le=1)
    label: str = Field(None)


class CamBase(BaseModel):
    """
    Base schema for a configurable dartboard setup.
    """

    card_name: str
    active: bool = False
    hardware_id: int


class Cam(CamBase):
    """Cam schema. This will also be saved in the mongo database as a collection."""

    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)
    active_task: Union[str, None] = None
    calibration_points: List[CalibrationPoint] = []


class CamCreate(CamBase):
    """Cam schema used to create new cam"""

    pass


class CamPatch(BaseModel):
    """Cam schema to patch a existing cam.
    Contains all fields which can be patched
    """

    card_name: Optional[str] = None
    active: Optional[bool] = None
    active_task: Optional[Union[str, None]] = None
    calibration_points: Optional[List[CalibrationPoint]] = None


class CamHardware(BaseModel):
    """Cam hardware schema.
    Represents a camera connected to the system.
    contains the current hardware id and the card name of the camera.
    """

    hardware_id: int
    card_name: str
