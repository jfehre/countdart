"""This worker module contains all celery task."""

import struct
import time

from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger
from vidgear.gears import CamGear

from countdart.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, base=AbortableTask)
def test_celery(self, string: str) -> str:
    """Celery task to test the worker and functions.
    Will sleep two seconds and then return a test string,
    which contains the input string

    Args:
        string: any input string

    Returns:
        test string which contains the input string
    """
    time.sleep(2)
    logger.info("Hi")
    return f"test task return {string}"


@celery_app.task(bind=True, base=AbortableTask)
def process_camera(self, cam: int):
    """Celery task to do the image processing of one camera.
    At the moment only a skeleton

    Args:
        cam: usb cam index
    """
    import redis

    r = redis.Redis(host="redis", port=6379)
    # start camera
    stream = CamGear(source=0).start()
    # create operators
    # endless loop. Needs to be canceled by celery
    while not self.is_aborted():
        frame = stream.read()
        # send frame
        # https://stackoverflow.com/a/60457732
        h, w, c = frame.shape
        print(frame.dtype)
        print(frame.shape)
        shape = struct.pack(">III", h, w, c)
        encoded = shape + frame.tobytes()
        r.set("img_2", encoded)

        time.sleep(2)
        print("Hallo")

    # task was aborted so shutdown gracefully
    stream.stop()
