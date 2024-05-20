"""This worker module contains all celery task."""

import time

from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.operators import (
    ChangeDetector,
    FpsCalculator,
    FrameGrabber,
    HomographyWarper,
)
from countdart.operators.img.bbox_detector import BBoxDetector
from countdart.operators.img.hough_line_detector import HoughLineDetector
from countdart.operators.img.result_visualizer import ResultVisualizer
from countdart.operators.size_classifier import SizeClassifier

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
    # initialize vars
    cam_db = schemas.Cam(**cam_db)

    # start camera
    cam = FrameGrabber.build_from_model(
        cam_db, config=cam_db.cam_config, redis_key=f"cam_{cam_db.id}"
    )
    cam.start()

    # create operators
    warper = None
    if cam_db.calibration_points:
        warper = HomographyWarper(
            cam_db.calibration_points,
            cam.image_size,
            redis_key=f"cam_{cam_db.id}",
        )
    motion = ChangeDetector(redis_key=f"cam_{cam_db.id}")
    bbox_detector = BBoxDetector()
    classifier = SizeClassifier()
    line_detector = HoughLineDetector()
    visualizer = ResultVisualizer(redis_key=f"cam_{cam_db.id}")
    fps_calculator = FpsCalculator(redis_key=f"cam_{cam_db.id}")

    # endless loop. Needs to be canceled by celery
    while not self.is_aborted():
        frame = cam()
        # calculate result
        warper(frame)
        motion_mask = motion(frame)
        bbox, size = bbox_detector(motion_mask)
        cls = classifier(size)
        if cls == "dart":
            line = line_detector(motion_mask, bbox)
            visualizer(frame, bbox, cls, line)
            # reset motion mask
            motion(frame, learning_rate=1)
        fps_calculator()

    # task was aborted so shutdown gracefully
    cam.teardown()
