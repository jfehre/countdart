"""Schema of a dartboard setup. Each dartboard contains
a list of cameras and a state (active).
May also contain more settings in the future.
"""
from typing import Dict, List, Optional, Union

from pydantic import ConfigDict, Field

from countdart.database.schemas.config import AllConfigModel

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
    type: str


class Dartboard(DartboardBase):
    """Dartboard schema. This will also be saved in the database as a table."""

    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)
    cams: List[PyObjectId] = []
    op_configs: Optional[Dict[str, List[AllConfigModel]]] = None
    active_task: Union[str, None] = None


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
    active_task: Optional[Union[str, None]] = None
    op_configs: Optional[Dict[str, List[AllConfigModel]]] = None
