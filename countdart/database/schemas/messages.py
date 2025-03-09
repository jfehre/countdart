"""
Schema for message objects. They are either send
to backend via redis or returned to the frontend.
"""
from typing import Optional

from countdart.database.schemas import DartThrowBase

from .base import BaseModel

__all__ = (
    "BaseMessage",
    "ResultMessage",
)


class BaseMessage(BaseModel):
    """
    Base class for messages.

    Attributes:
        type (str): The type of the message.
        content (str): The content of the message.
    """

    type: str
    content: str


class ResultMessage(BaseMessage):
    """
    Message class for result messages.

    Attributes:
        type (str): The type of the message, default is "result".
        content (Optional[DartThrowBase]): The content of the message, default is None.
    """

    type: str = "result"
    cls: str
    content: Optional[DartThrowBase] = None
