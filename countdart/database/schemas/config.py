""" Schemas for config types"""

from typing import Any, List, Optional, Union

from pydantic import ValidationInfo, field_validator

from .base import BaseModel

__all__ = (
    "ConfigBaseModel",
    "IntConfigModel",
    "BooleanConfigModel",
    "SelectConfigModel",
    "DeleteConfigModel",
    "AllConfigModel",
)


class ConfigBaseModel(BaseModel):
    """Schema for configs base"""

    name: str
    default_value: Any
    description: Optional[str] = None


class IntConfigModel(ConfigBaseModel):
    """Schema for a config based on integers"""

    type: str = "int"
    max_value: int
    min_value: int
    default_value: int
    value: Optional[int] = None

    @field_validator("type")
    def check_type(cls, v, info):
        """validator to check if type is int"""
        if v != "int":
            raise ValueError("invalid type")
        return v

    @field_validator("value")
    def ensure_value(cls, v: any, info: ValidationInfo):
        """validator to check if value is within given min max range"""
        # check type again, because all fields will be validated
        if "type" not in info.data or info.data["type"] != "int":
            raise ValueError("invalid type")
        if v and not info.data["min_value"] <= v <= info.data["max_value"]:
            raise ValueError(
                f"Value {v} needs to be higher than {info.data['min_value']} "
                + "and lower than {info.data['max_value']}"
            )
        return v


class BooleanConfigModel(ConfigBaseModel):
    """Schema for boolean config model"""

    type: str = "bool"
    default_value: bool
    value: Optional[bool] = None

    @field_validator("type")
    def check_type(cls, v):
        """validator to check if type is bool"""
        if v != "bool":
            raise ValueError("invalid type")
        return v


class SelectConfigModel(ConfigBaseModel):
    """Schema model for selection based configs"""

    type: str = "select"
    data: List[Any]
    value: Optional[Any] = None

    @field_validator("type")
    def check_type(cls, v):
        """validator to check if type is select"""
        if v != "select":
            raise ValueError("invalid type")
        return v


class DeleteConfigModel(ConfigBaseModel):
    """Schema model to delete config. Seperate model needed to distinguish
    between update and delete action."""

    type: str = "_delete_"

    @field_validator("type")
    def check_type(cls, v):
        """validator to check if type is _delete_"""
        if v != "_delete_":
            raise ValueError("invalid type")
        return v


# Include the most specific type first, followed by the less specific types
AllConfigModel = Union[
    BooleanConfigModel, IntConfigModel, SelectConfigModel, DeleteConfigModel
]
