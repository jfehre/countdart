"""
Creates a singleton celery app, which can be used project wide,
to define tasks which are executed by a seperate celery worker.

Celery needs a worker, which should be started as a docker service defined
in docker-compose as celeryworker. Alternatively you can create a worker
with executing `celery -A countdart.celery_app.celery_app worker --loglevel=INFO`
in a seperate terminal.
"""

from celery import Celery

CELERY_BROKER = "sqla+sqlite:///db.sqlite"
CELERY_BACKEND = "db+sqlite:///db.sqlite"


def make_celery(app_name: str) -> Celery:
    """Creates a celery app to manage tasks.

    :param app_name: celery app name
    :return: a celery app object
    """
    celery_app = Celery(
        app_name,
        broker=CELERY_BROKER,
        backend=CELERY_BACKEND,
        include=["countdart.worker"],
    )
    return celery_app


celery_app = make_celery("countdart")
