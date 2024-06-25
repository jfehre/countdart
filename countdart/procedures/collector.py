"""This module contains the default/standard algorithm to detect darts."""


import json
from time import sleep
from typing import Dict, List, Tuple

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
    def majority(items: List[str]) -> Tuple[str, int]:
        """Return value with most occurence in given list
        Returns the value as well as the number of occurence

        Args:
            items (List[str]): list of strings

        Returns:
            Tuple[str, int]: value with most occurence and its count
        """
        max_count = -1
        value = ""
        for x in items:
            count = items.count(x)
            if count > max_count:
                max_count = count
                value = x
        return value, max_count

    @staticmethod
    def get_max(items: Dict[str, Dict], compare_key: str) -> Tuple[str, float]:
        """returns key if dict with maximum value in in the compare key

        Args:
            items (Dict[str, Dict]): Dict of dicts
            compare_key (str): key to compare in the nested dict

        Returns:
            Tuple[str, float]: key and value of the maximum number
        """
        max_num = -1
        key = ""
        for k, value in items.items():
            if value[1][compare_key] > max_num:
                max_num = value[1][compare_key]
                key = k
        return key, max_num

    def run(self, dartboard_db: schemas.Dartboard):
        """start image processing to detect darts."""
        # initialize vars
        dartboard_db = schemas.Dartboard(**dartboard_db)

        r = redis.Redis(host="redis", port=6379)

        # create result key
        all_results = dict.fromkeys(dartboard_db.cams, None)

        # delete redis list and old results
        for cam_id in dartboard_db.cams:
            key = f"cam_{cam_id}_ResultPublisher"
            r.delete(key)

        # endless loop. Needs to be canceled by celery
        while not self.is_aborted():
            # check for result
            for cam_id in dartboard_db.cams:
                key = f"cam_{cam_id}_ResultPublisher"
                # result = r.get(key)
                result = r.rpop(key)
                if result is not None:
                    all_results[cam_id] = json.loads(result)
            # check if all results are collected
            if None not in all_results.values():
                # check if all classes are same
                cls = [x[0] for x in all_results.values()]
                if self.all_same(cls):
                    if cls[0] == "hand":
                        print("HAND")
                    elif cls[0] == "dart":
                        scores = [x[1]["score"] for x in all_results.values()]
                        best_conf_key, _ = self.get_max(all_results, "conf")
                        # check if there is a majority score
                        max_score, count = self.majority(scores)
                        if count > len(scores) / 2:
                            print(f"DART {max_score}")
                        else:
                            # get max conf score
                            print(f"DART {all_results[best_conf_key][1]['score']}")
                else:
                    print("some cameras show different results")

                # reset results
                all_results = dict.fromkeys(dartboard_db.cams, None)
            else:
                sleep(0.1)

    def __call__(self, *args, **kwargs):
        """will call run"""
        return self.run(*args, **kwargs)


# Add to celery tasks
celery_app.register_task(MainCollector)
