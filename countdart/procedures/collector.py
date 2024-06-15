"""This module contains the default/standard algorithm to detect darts."""

from time import sleep

import redis
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from countdart.celery_app import celery_app
from countdart.database import schemas

logger = get_task_logger(__name__)


class MainCollector(AbortableTask):
    """Main task to collect results of procedures."""

    def __init__(self):
        # use class name as name, otherwise celery will not find the task
        self.name = self.__name__

    def run(self, dartboard_db: schemas.Dartboard):
        """start image processing to detect darts."""
        # initialize vars
        dartboard_db = schemas.Dartboard(**dartboard_db)

        r = redis.Redis(host="redis", port=6379)

        # endless loop. Needs to be canceled by celery
        while not self.is_aborted():
            # check for result
            for cam_id in dartboard_db.cams:
                key = f"cam_{cam_id}_FpsCalculator"
                result = r.get(key)
                print(result)

            sleep(1)

    def __call__(self, *args, **kwargs):
        """will call run"""
        return self.run(*args, **kwargs)


# Add to celery tasks
celery_app.register_task(MainCollector)
