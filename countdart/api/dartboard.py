"""REST API endpoint for dartboards.
Used to retrieve, create, update and delete dartboards
"""

import io
import struct
from typing import List

import numpy as np
import redis
from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, HTTPException, Response
from PIL import Image

from countdart.celery_app import celery_app
from countdart.database import schemas
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


@router.get("/{dartboard_id}/start")
def start_dartboard(
    dartboard_id: int,
) -> schemas.TaskOut:
    """starts the worker tasks for the dartboard

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    r = process_camera.delay(0)
    return schemas.TaskOut.celery_to_task_out(r)


@router.get("/{dartboard_id}/stop")
def stop_dartboard(
    dartboard_id: int,
):
    """Will stop all active worker tasks at the moment

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    # get all running celery tasks and stop them
    i = celery_app.control.inspect()
    active_tasks = i.active()
    for key, task in active_tasks.items():
        res = AbortableAsyncResult(task[0]["id"], app=celery_app)
        res.abort()
    return "stopped"


@router.get("/{dartboard_id}/frame")
def get_image(
    dartboard_id: int,
) -> Response:
    """Returns the current frame of the camera

    Args:
        dartboard_id (int): id of the dartboard
    """
    r = redis.Redis(host="redis", port=6379)
    encoded = r.get("img_2")
    h, w, c = struct.unpack(">III", encoded[:12])
    # Add slicing here, or else the array would differ from the original
    frame = np.frombuffer(encoded[12:], dtype=np.uint8).reshape(h, w, c)
    img = Image.fromarray(frame)
    with io.BytesIO() as buf:
        img.save(buf, format="PNG")
        im_bytes = buf.getvalue()

    return Response(im_bytes, media_type="image/png")
