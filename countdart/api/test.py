"""Test routes to test some functions. May be temporar."""

from typing import Union

from celery.result import AsyncResult
from fastapi import APIRouter
from pydantic import BaseModel

from countdart.celery_app import celery_app
from countdart.worker import test_celery

router = APIRouter(prefix="/test", tags=["test"])


class TaskOut(BaseModel):
    """Schema for celery task outputs"""

    id: str
    status: str
    result: Union[str, None]


@router.get("")
def get_hello_world():
    """returns "Hello World" to test if endpoints are working

    Returns:
        string with "Hello World"
    """
    return "Hello World"


@router.get("/task/start")
def start_task() -> TaskOut:
    """Starts a celery task to test if it is working

    Returns:
        Task information
    """
    r = test_celery.delay("hello")
    return _to_task_out(r)


@router.get("/task/status/{task_id}")
def status(task_id: str) -> TaskOut:
    """Get the status of a celery task with a given id

    Args:
        task_id: id of the task

    Returns:
        Task information
    """
    r = celery_app.AsyncResult(task_id)
    return _to_task_out(r)


def _to_task_out(r: AsyncResult) -> TaskOut:
    """converts an AsyncResult from Celery to a readable output schema

    Args:
        r: AsyncResult

    Returns:
        Model for task output
    """
    return TaskOut(
        id=r.task_id, status=r.status, result=r.traceback if r.failed() else r.result
    )
