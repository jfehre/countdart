"""This module contains a debug procedure which will just record
the input source and saves it as an mp4 directly in your workspace.
The saved videos can later be used for easier debugging and testing.
"""

from typing import Dict, List

from celery.utils.log import get_task_logger
from pydantic import TypeAdapter

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.database.schemas.config import AllConfigModel
from countdart.operators import FpsCalculator, FrameGrabber, VideoWriter
from countdart.procedures.base import PROCEDURES, BaseProcedure

logger = get_task_logger(__name__)


@PROCEDURES.register_class
class DebugRecorder(BaseProcedure):
    """Debug recorder/procedure to save input stream as mp4 video."""

    @property
    def operators(self):
        """Will return all properties used in this procedure.
        This list needs to be initialized manually with all
        operators used in the run method, the user may want to
        change.
        """
        return [
            VideoWriter,
            FpsCalculator,
        ]

    def run(self, cam_db: schemas.Cam, op_configs: Dict[str, List]):
        """start image processing to detect darts."""
        # convert configs
        for op, op_conf in op_configs.items():
            op_configs[op] = [
                TypeAdapter(AllConfigModel).validate_python(c) for c in op_conf
            ]
        # initialize vars
        cam_db = schemas.Cam(**cam_db)

        # start camera
        cam = FrameGrabber.build_from_model(
            cam_db, config=cam_db.cam_config, redis_key=f"cam_{cam_db.id}"
        )
        cam.start()

        # create operators
        writer = VideoWriter(f"cam_{cam_db.id}_output.mp4")
        fps_calculator = FpsCalculator(redis_key=f"cam_{cam_db.id}")

        while not self.is_aborted():
            frame = cam()
            writer(frame)
            fps_calculator()

        # task was aborted so shutdown gracefully
        cam.teardown()


# Add to celery tasks
celery_app.register_task(DebugRecorder)
