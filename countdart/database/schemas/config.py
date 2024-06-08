""" Schemas for config types"""

from typing import Any, List, Optional, Union

from pydantic import Field, ValidationInfo, field_validator

from .base import BaseModel

__all__ = (
    "ConfigBaseModel",
    "IntConfigModel",
    "FloatConfigModel",
    "BooleanConfigModel",
    "SelectConfigModel",
    "DeleteConfigModel",
    "AllConfigModel",
)


class ConfigBaseModel(BaseModel):
    """Schema for configs base
    Each config needs:
    - name: define config name. Should be the same as
    the attribute in the operator
    - type: string with the type. We check this string
    in each sub model, because otherwise pydantic is not
    able to choose the correct model type when creating
    models from dict.
    - default value
    - description (Optional)
    - value: We define value in base model, so we can
    create an init function which initializes an existing
    configmodel (defaultmodel) with a value if name matches

    """

    name: str
    type: str
    default_value: Any
    description: Optional[str] = None


class IntConfigModel(ConfigBaseModel):
    """Schema for a config based on integers"""

    type: str = "int"
    max_value: int
    min_value: int
    default_value: int
    value: Optional[int] = Field(default=None, validate_default=True)

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
                + f"and lower than {info.data['max_value']}"
            )
        return v if v else info.data["default_value"]


class FloatConfigModel(ConfigBaseModel):
    """Schema for a config based on floats"""

    type: str = "float"
    max_value: float
    min_value: float
    default_value: float
    value: Optional[float] = Field(default=None, validate_default=True)

    @field_validator("type")
    def check_type(cls, v, info):
        """validator to check if type is float"""
        if v != "float":
            raise ValueError("invalid type")
        return v

    @field_validator("value")
    def ensure_value(cls, v: any, info: ValidationInfo):
        """validator to check if value is within given min max range"""
        # check type again, because all fields will be validated
        if "type" not in info.data or info.data["type"] != "float":
            raise ValueError("invalid type")
        if v and not info.data["min_value"] <= v <= info.data["max_value"]:
            raise ValueError(
                f"Value {v} needs to be higher than {info.data['min_value']} "
                + f"and lower than {info.data['max_value']}"
            )
        return v if v else info.data["default_value"]


class BooleanConfigModel(ConfigBaseModel):
    """Schema for boolean config model"""

    type: str = "bool"
    default_value: bool
    value: Optional[bool] = Field(default=None, validate_default=True)

    @field_validator("type")
    def check_type(cls, v):
        """validator to check if type is bool"""
        if v != "bool":
            raise ValueError("invalid type")
        return v

    @field_validator("value", mode="after")
    def ensure_value(cls, v, info):
        """ensure value to be not None, by setting it to default value"""
        # check type again, because all fields will be validated
        if "type" not in info.data or info.data["type"] != "bool":
            raise ValueError("invalid type")
        return v if v else info.data["default_value"]


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
    BooleanConfigModel,
    IntConfigModel,
    FloatConfigModel,
    SelectConfigModel,
    DeleteConfigModel,
]
