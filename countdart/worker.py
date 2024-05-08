"""This worker module contains all celery task."""

import logging
import time

from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.io import USBCam
from countdart.operators.change_detector import ChangeDetector
from countdart.operators.fps_calculator import FpsCalculator
from countdart.operators.homography_warper import HomographyWarper
from countdart.utils.misc import encode_numpy

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
def process_camera(self, cam_db: schemas.Cam):
    """Celery task to do the image processing of one camera.
    At the moment only a skeleton

    Args:4
        cam: usb cam index
    """
    import redis

    # initialize vars
    cam_db = schemas.Cam(**cam_db)
    r = redis.Redis(host="redis", port=6379)

    # start camera
    cam = USBCam(cam_db.hardware_id)
    cam.start()

    # create operators
    img_operators = []
    if cam_db.calibration_points:
        img_operators.append(
            HomographyWarper(
                cam_db.calibration_points,
                cam.image_size,
                redis_key=f"cam_{cam_db.id}_img_warped",
            )
        )
    img_operators.append(ChangeDetector(redis_key=f"cam_{cam_db.id}_img_motion"))
    fps_calculator = FpsCalculator(redis_key=f"cam_{cam_db.id}_fps")

    # endless loop. Needs to be canceled by celery
    while not self.is_aborted():
        frame = cam.get_frame()
        # send frame
        logging.debug(frame.shape)
        encoded = encode_numpy(frame)
        r.set(f"cam_{cam_db.id}_img_raw", encoded)
        # add image operators
        for operator in img_operators:
            operator(frame)
        fps_calculator()

    # task was aborted so shutdown gracefully
    cam.stop()
