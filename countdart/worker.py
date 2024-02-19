"""This worker module contains all celery task."""

import time

from celery.contrib.abortable import AbortableTask

from countdart.celery_app import celery_app


@celery_app.task
def test_celery(string: str) -> str:
    """Celery task to test the worker and functions.
    Will sleep two seconds and then return a test string,
    which contains the input string

    Args:
        string: any input string

    Returns:
        test string which contains the input string
    """
    time.sleep(2)
    return f"test task return {string}"


@celery_app.task(bind=True, base=AbortableTask)
def process_camera(self, cam: int):
    """Celery task to do the image processing of one camera.
    At the moment only a skeleton

    Args:
        cam: usb cam index
    """
    # start camera
    # create operators
    # endless loop. Needs to be canceled by celery
    while not self.is_aborted():
        time.sleep(5)
        print("Hallo")

    # task was aborted so shutdown gracefully
