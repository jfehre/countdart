"""REST API endpoint for dartboards.
Used to retrieve, create, update and delete dartboards
"""

from typing import List

from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, HTTPException

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.database.crud import cam as cam_crud
from countdart.database.crud import dartboard as crud
from countdart.database.db import NameAlreadyTakenError, NotFoundError
from countdart.worker import process_camera

router = APIRouter(prefix="/dartboards", tags=["dartboard"])


@router.get("", response_model_by_alias=False)
def get_dartboards() -> List[schemas.Dartboard]:
    """Retrieve all dartboards

    Returns:
        List of dartboards
    """
    try:
        result = crud.get_dartboards()
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.post("", response_model_by_alias=False)
def create_dartboard(dartboard: schemas.DartboardCreate) -> schemas.Dartboard:
    """Create new dartboard

    Returns:
        Created dartboard
    """
    try:
        result = crud.create_dartboard(dartboard)
    except NameAlreadyTakenError as e:
        raise HTTPException(409) from e
    return result


@router.patch("/{dartboard_id}", response_model_by_alias=False)
def update_dartboard(
    dartboard_id: schemas.IdString,
    dartboard: schemas.DartboardPatch,
) -> schemas.Dartboard:
    """Retrieve dartboard with given id

    Returns:
        Dartboard with given id
    """
    try:
        updated = crud.update_dartboard(dartboard_id, dartboard)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return updated


@router.delete("/{dartboard_id}", response_model_by_alias=False)
def delete_dartboard(dartboard_id: schemas.IdString):
    """Delete dartboard with given id

    Returns:
        Dartboard with given id
    """
    try:
        crud.delete_dartboard(dartboard_id)
    except NotFoundError as e:
        raise HTTPException(404) from e


@router.get("/{dartboard_id}", response_model_by_alias=False)
def get_dartboard(dartboard_id: schemas.IdString) -> schemas.Dartboard:
    """Retrieve dartboard with given id

    Returns:
        Dartboard with given id
    """
    try:
        result = crud.get_dartboard(dartboard_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.get("/{dartboard_id}/start", response_model_by_alias=False)
def start_dartboard(
    dartboard_id: schemas.IdString,
) -> schemas.Dartboard:
    """starts all camera of dartboard and set active to True

    Returns:
        schemas.Dartboard: Updated Dartboard
    """
    try:
        result = crud.get_dartboard(dartboard_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    # start cams
    active_tasks = []
    for cam_id in result.cams:
        cam = cam_crud.get_cam(cam_id)
        if cam.active:
            active_tasks.append(cam.active_task)
        else:
            r = process_camera.delay(cam.hardware_id, cam_id)
            active_tasks.append(r.id)
            cam_crud.update_cam(cam_id, schemas.CamPatch(active=True, active_task=r.id))
    # update active tasks
    result = crud.update_dartboard(
        dartboard_id,
        schemas.DartboardPatch(active_celery_tasks=active_tasks, active=True),
    )
    return result


@router.get("/{dartboard_id}/stop")
def stop_dartboard(
    dartboard_id: schemas.IdString,
) -> schemas.Dartboard:
    """Will stop all active worker tasks at the moment

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    try:
        result = crud.get_dartboard(dartboard_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    # get active tasks and stop them
    active_tasks = result.active_celery_tasks
    for task_id in active_tasks:
        res = AbortableAsyncResult(task_id, app=celery_app)
        res.abort()
    # set to inactive
    for cam in result.cams:
        cam_crud.update_cam(cam, schemas.CamPatch(active=False, active_task=None))
    # update active tasks
    result = crud.update_dartboard(
        dartboard_id, schemas.DartboardPatch(active_celery_tasks=[], active=False)
    )
    return result
