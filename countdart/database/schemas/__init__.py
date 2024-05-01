""".. _`basics tutorial`: https://sqlmodel.tiangolo.com/
.. _`tutorial about using sqlmodel in conjunction with FastAPI`:
https://sqlmodel.tiangolo.com/tutorial/fastapi/update/

This package contains all models/schemas, which are exchanged over
the API between the frontend and the backend.

We use the sqlmodel library by tiangolo.
Before changing anything, it is probably best to read through
the `basics tutorial`_ (only takes about 30 minutes).

and the `tutorial about using sqlmodel in conjunction with FastAPI`_.

If you still want/have to start right away, some non-obvious tips from
the tutorial are:

 1. Only inherit from data models, don't inherit from table models.
 2. The ID of the table model should be optional, since before adding
    it to the table, it won't have an id.
    But the read/response model should have a required/guaranteed ID,
    such that the client can rely on always getting an ID.

"""
from .base import BaseModel, IdString, PyObjectId  # noqa: F401
from .cam import (  # noqa: F401
    CalibrationPoint,
    Cam,
    CamBase,
    CamCreate,
    CamHardware,
    CamPatch,
)
from .dartboard import (  # noqa: F401
    Dartboard,
    DartboardBase,
    DartboardCreate,
    DartboardPatch,
)
from .task import TaskOut  # noqa: F401
