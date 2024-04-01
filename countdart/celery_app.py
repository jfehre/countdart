"""Creates a singleton celery app, which can be used project wide,
to define tasks which are executed by a seperate celery worker.

Celery needs a worker, which should be started as a docker service defined
in docker-compose as celeryworker.
Alternatively you can create a worker with executing
`celery -A countdart.celery_app.celery_app worker --loglevel=INFO`
in a seperate terminal. This also helps with debugging, because
you are able to see logging information

If you want to better debug celery task install flower `pip install flower`
and use command `celery -A countdart.celery_app.celery_app flower`
to start a task manager
"""

from celery import Celery

from countdart.settings import settings


def make_celery(app_name: str) -> Celery:
    """Creates a celery app to manage tasks.

    Args:
        app_name: celery app name

    Returns:
        a celery app object
    """
    celery_app = Celery(
        app_name,
        broker=settings.CELERY_BROKER,
        backend=settings.CELERY_BACKEND,
        include=["countdart.worker"],
    )
    return celery_app


celery_app = make_celery("countdart")
