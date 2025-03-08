"""This module contains the default/standard algorithm to detect darts."""


import json
import time
from time import sleep
from typing import List, Tuple

import redis
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from countdart.celery_app import celery_app
from countdart.database import schemas
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
        all_results = dict.fromkeys(dartboard_db.cams, None)

        # delete redis list and old results
        for cam_id in dartboard_db.cams:
            key = f"cam_{cam_id}_ResultPublisher"
            r.delete(key)

        receive_time = 0
        timout_sec = 1
        prev_cls = "none"

        # endless loop. Needs to be canceled by celery
        while not self.is_aborted():
            # check for result
            for cam_id in dartboard_db.cams:
                key = f"cam_{cam_id}_ResultPublisher"
                result = r.get(key)
                if result and result != "":
                    all_results[cam_id] = json.loads(result)
                    receive_time = time.time()

            # conditions for result publishing
            completed = None not in all_results.values()
            timout = receive_time != 0 and time.time() - receive_time > timout_sec

            if completed or timout:
                # get majority class
                cls, _ = self.majority([x[0] for x in all_results.values() if x])
                if cls == "hand" and prev_cls != "hand":
                    r.set(result_key, json.dumps(["hand"]))
                elif cls == "dart":
                    # get all scores
                    scores = []
                    confs = []
                    for result in all_results.values():
                        if result and result[0] == "dart":
                            scores.append(result[1]["score"])
                            confs.append(result[1]["conf"])
                    # check if there is a majority score
                    _, indices = self.majority(scores)
                    if len(indices) > len(scores) / 2:
                        r.set(
                            result_key,
                            json.dumps(all_results[dartboard_db.cams[indices[0]]]),
                        )
                    else:
                        # get max conf score
                        best_result = all_results[
                            dartboard_db.cams[indices[confs.index(max(confs))]]
                        ]
                        r.set(result_key, json.dumps(best_result))
                elif cls == "none" and prev_cls != "none":
                    r.set(result_key, json.dumps(["none"]))

                # reset results
                all_results = dict.fromkeys(dartboard_db.cams, None)
                for cam_id in dartboard_db.cams:
                    key = f"cam_{cam_id}_ResultPublisher"
                    # delete key from redis
                    result = r.set(key, "")
                receive_time = 0
                prev_cls = cls
            else:
                sleep(0.1)

    def __call__(self, *args, **kwargs):
        """will call run"""
        return self.run(*args, **kwargs)


# Add to celery tasks
celery_app.register_task(MainCollector)
