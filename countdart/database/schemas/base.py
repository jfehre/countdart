""" Base schemas. Contains a BaseModel and
IdString/PyObjectId which are used for mongodb crud operations
"""
from typing import NewType

from pydantic import BaseModel as PydanticBaseModel
from pydantic import BeforeValidator
from typing_extensions import Annotated

__all__ = ("BaseModel", "IdString", "PyObjectId")

IdString = NewType("IdString", str)
PyObjectId = Annotated[str, BeforeValidator(str)]


class BaseModel(PydanticBaseModel):
    """
    Base model. Not used yet, but can be used to add common fields later on
    """

    pass
