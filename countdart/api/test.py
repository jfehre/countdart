"""Test routes to test some functions. May be temporar."""

from fastapi import APIRouter

from countdart.celery_app import celery_app
from countdart.database.schemas import TaskOut
from countdart.procedures.standard import test_celery

router = APIRouter(prefix="/test", tags=["test"])


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
    return TaskOut.celery_to_task_out(r)


@router.get("/task/status/{task_id}")
def status(task_id: str) -> TaskOut:
    """Get the status of a celery task with a given id

    Args:
        task_id: id of the task

    Returns:
        Task information
    """
    r = celery_app.AsyncResult(task_id)
    return TaskOut.celery_to_task_out(r)
