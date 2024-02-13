"""
Schema of a dartboard setup. Each dartboard contains
a list of cameras and a state (active).
May also contain more settings in the future.
"""
from typing import List, Optional

from sqlmodel import Field, SQLModel

__all__ = ("Dartboard", "DartboardBase")


class DartboardBase(SQLModel):
    """
    Base schema for a configurable dartboard setup.
    """

    name: str = Field(sa_column_kwargs={"unique": True})
    active: bool


class Dartboard(DartboardBase, table=True):
    """
    Dartboard schema. This will also be saved in the database as a table.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    cameras: Optional[List[int]]
