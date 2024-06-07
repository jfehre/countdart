"""REST API endpoint for dartboards.
Used to retrieve, create, update and delete dartboards
"""

import json
from typing import List

import redis
from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, HTTPException, Query

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.database.crud import cam as cam_crud
from countdart.database.crud import dartboard as crud
from countdart.database.db import NameAlreadyTakenError, NotFoundError
from countdart.procedures.base import PROCEDURES
from countdart.utils.misc import update_config_dict

router = APIRouter(prefix="/dartboards", tags=["Dartboard"])


@router.get("/types")
def get_procedure_types() -> List[str]:
    """Will return available types from registry"""
    return PROCEDURES.registry.keys()


@router.get("", response_model_by_alias=False)
def get_dartboards(
    id_list: List[schemas.IdString] = Query(None),
    cam: schemas.IdString = Query(None),
) -> List[schemas.Dartboard]:
    """Retrieve all dartboards

    Args:
        id_list (List[schemas.IdString], optional):
        If given only return dartboards within this list.
        cam (schemas.IdString, optional): return only
        dartboards, which contain given cam id

    Returns:
        List of dartboards
    """
    try:
        result = crud.get_dartboards(id_list=id_list, cam=cam)
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
        # merge config dict and update
        if dartboard.op_configs is not None:
            old_configs = crud.get_dartboard(dartboard_id).op_configs
            updated_configs = update_config_dict(old_configs, dartboard.op_configs)
            dartboard.op_configs = updated_configs
        updated = crud.update_dartboard(dartboard_id, dartboard)
        # use redis to apply config to all worker processes
        r = redis.Redis(host="redis", port=6379)
        cams = cam_crud.get_cams(id_list=dartboard.cams)
        # communicate with each procedure in each cam
        for cam in cams:
            r.set(
                f"cam_{cam.id}_config",
                json.dumps(updated.model_dump()["op_configs"]),
            )
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
        # else:
        # r = process_camera.delay(cam.source, cam_id)
        # active_tasks.append(r.id)
        # cam_crud.update_cam(cam_id, schemas.CamPatch(active=True, active_task=r.id))
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
