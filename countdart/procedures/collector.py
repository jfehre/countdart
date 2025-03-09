"""This module contains the default/standard algorithm to detect darts."""


import json
import time
from time import sleep
from typing import Dict, List, Optional, Tuple

import redis
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.database.schemas import ResultMessage
from countdart.settings import settings

logger = get_task_logger(__name__)


class MainCollector(AbortableTask):
    """Main task to collect results of procedures."""

    def __init__(self):
        # use class name as name, otherwise celery will not find the task
        self.name = self.__name__

    @staticmethod
    def all_same(items: List[str]) -> bool:
        """check if all items in list are the same

        Args:
            items (List[str]): list of strings

        Returns:
            bool: true if all items are same, else false
        """
        return all(x == items[0] for x in items)

    @staticmethod
    def majority(items: List[str]) -> Tuple[str, List[int]]:
        """Return value with most occurence in given list
        Returns the value as well as indices of all occurence

        Args:
            items (List[str]): list of strings

        Returns:
            Tuple[str, List[int]]: value with most occurence and its count
        """
        max_count = -1
        value = ""
        for x in items:
            count = items.count(x)
            if count > max_count:
                max_count = count
                value = x
        return value, [i for i, x in enumerate(items) if x == value]

    def run(self, dartboard_db: schemas.Dartboard):
        """start image processing to detect darts."""
        # initialize vars
        dartboard_db = schemas.Dartboard(**dartboard_db)

        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        # key where results are published
        result_key = f"dartboard_{dartboard_db.id}_result"

        # create result key
        # The result is a dict for each cam with the result and if it was published
        all_results: Dict[str, Optional[ResultMessage]]
        all_results = dict.fromkeys(dartboard_db.cams, None)
        result_publish_status = dict.fromkeys(dartboard_db.cams, True)
        prev_results = dict.fromkeys(dartboard_db.cams, None)

        # delete redis list and init prev_result
        # prev results contains tuple of result and if it was published
        for cam_id in dartboard_db.cams:
            r.delete(f"cam_{cam_id}_ResultPublisher")

        # timeout variables to retrieve results from all cams
        receive_time = 0
        timout_sec = 1

        # endless loop. Needs to be canceled by celery
        while not self.is_aborted():
            # check for new result
            for cam_id in dartboard_db.cams:
                result = r.get(f"cam_{cam_id}_ResultPublisher")
                result = ResultMessage(**json.loads(result)) if result else None
                if result and result != prev_results[cam_id]:
                    all_results[cam_id] = result
                    prev_results[cam_id] = result
                    result_publish_status[cam_id] = False
                    receive_time = time.time()

            # conditions for result publishing
            all_results_unpublished = not any(
                [x for x in result_publish_status.values()]
            )
            wait_timout = receive_time != 0 and time.time() - receive_time > timout_sec

            if all_results_unpublished or wait_timout:
                # get majority class
                majority_cls, _ = self.majority(
                    [x.cls for x in all_results.values() if x]
                )
                if majority_cls == "hand":
                    r.set(result_key, ResultMessage(cls="hand").model_dump_json())
                elif majority_cls == "dart":
                    # get all scores and also use majority
                    scores = [
                        x.content.score for x in all_results.values() if x.content
                    ]
                    confs = [
                        x.content.confidence for x in all_results.values() if x.content
                    ]
                    # check if there is a majority score
                    _, indices = self.majority(scores)
                    if len(indices) > len(scores) / 2:
                        r.set(
                            result_key,
                            all_results[
                                dartboard_db.cams[indices[0]]
                            ].model_dump_json(),
                        )
                    else:
                        # get max conf score
                        best_result = all_results[
                            dartboard_db.cams[indices[confs.index(max(confs))]]
                        ]
                        r.set(result_key, best_result.model_dump_json())
                elif majority_cls == "none":
                    r.set(result_key, ResultMessage(cls="none").model_dump_json())

                receive_time = 0
            else:
                sleep(0.1)

    def __call__(self, *args, **kwargs):
        """will call run"""
        return self.run(*args, **kwargs)


# Add to celery tasks
celery_app.register_task(MainCollector)
