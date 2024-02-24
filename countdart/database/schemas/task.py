"""
Models for celery tasks
"""

from typing import Union

from celery.result import AsyncResult

from .base import BaseModel

__all__ = ("TaskOut",)


class TaskOut(BaseModel):
    """Schema for celery task outputs"""

    id: str
    status: str
    result: Union[str, None]

    @classmethod
    def celery_to_task_out(cls, r: AsyncResult):
        """Create a new task out model from celery asyncresult

        Args:
            r (AsyncResult): celery result

        Returns:
            Self: New TaskOut model
        """
        return cls(
            id=r.task_id,
            status=r.status,
            result=r.traceback if r.failed() else r.result,
        )
