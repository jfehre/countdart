"""REST API endpoint for cams.
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
from countdart.database.crud import cam as crud
from countdart.database.db import NameAlreadyTakenError, NotFoundError
from countdart.io import USBCam
from countdart.worker import process_camera

router = APIRouter(prefix="/cams", tags=["Camera"])


@router.get("", response_model_by_alias=False)
def get_cams() -> List[schemas.Cam]:
    """Retrieve all database cams

    Returns:
        List of cams
    """
    try:
        result = crud.get_cams()
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.post("", response_model_by_alias=False)
def create_cam(cam: schemas.CamCreate) -> schemas.Cam:
    """Create new cam

    Returns:
        Created cam
    """
    try:
        result = crud.create_cam(cam)
    except NameAlreadyTakenError as e:
        raise HTTPException(409) from e
    return result


@router.patch("/{cam_id}", response_model_by_alias=False)
def update_cam(
    cam_id: schemas.IdString,
    cam: schemas.CamPatch,
) -> schemas.Cam:
    """Retrieve cam with given id

    Returns:
        cam with given id
    """
    try:
        updated = crud.update_cam(cam_id, cam)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return updated


@router.delete("/{cam_id}", response_model_by_alias=False)
def delete_cam(
    cam_id: schemas.IdString,
):
    """Delete cam with given id

    Returns:
        cam with given id
    """
    try:
        crud.delete_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e


@router.get("/{cam_id}", response_model_by_alias=False)
def get_cam(cam_id: schemas.IdString) -> schemas.Cam:
    """Retrieve cam with given id

    Returns:
        Cam with given id
    """
    try:
        result = crud.get_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.get("/find")
def find_cams() -> List[schemas.CamHardware]:
    """Find all available cams connected to the system

    Returns:
        List of available cams
    """
    cams = USBCam.get_available_cams()
    # convert to CamHardware
    result = []
    for cam in cams:
        result.append(schemas.CamHardware(**cam))
    return result


@router.get("/{cam_id}/start")
def start_cam(
    cam_id: int,
) -> schemas.TaskOut:
    """starts the worker tasks for the cam

    Args:
        session (Session, optional): sql session. Defaults to Depends(get_session).

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    r = process_camera.delay(0)
    return schemas.TaskOut.celery_to_task_out(r)


@router.get("/{cam_id}/stop")
def stop_cam(
    cam_id: int,
):
    """Will stop all active worker tasks at the moment

    Args:
        session (Session, optional): sql session. Defaults to Depends(get_session).

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


@router.get("/{cam_id}/frame")
def get_image(
    cam_id: int,
) -> Response:
    """Returns the current frame of the camera

    Args:
        cam_id (int): id of the dartboard
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
