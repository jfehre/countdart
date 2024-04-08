"""REST API endpoint for cams.
Used to retrieve, create, update and delete dartboards
"""

import asyncio
import base64
import io
from typing import List

import redis
from celery.contrib.abortable import AbortableAsyncResult
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from PIL import Image

from countdart.celery_app import celery_app
from countdart.database import schemas
from countdart.database.crud import cam as crud
from countdart.database.db import NameAlreadyTakenError, NotFoundError
from countdart.io import USBCam
from countdart.utils.misc import decode_numpy
from countdart.worker import process_camera

router = APIRouter(prefix="/cams", tags=["Camera"])


@router.websocket("/ws/{cam_id}/live")
async def websocket_endpoint(cam_id: schemas.IdString, websocket: WebSocket):
    await websocket.accept()
    encoded_array = None
    try:
        while True:
            # Add this statement to yield back control to allow
            # context switch and serve multiple request concurrently
            # not working
            await asyncio.sleep(0)
            # Get current values from key
            r = redis.Redis(host="redis", port=6379)
            encoded = r.get(f"img_{cam_id}")
            # check if value changed, otherwise no update needs to be send
            if encoded_array == encoded:
                continue
            else:
                encoded_array = encoded
            # decode numpy array to base64 string
            frame = decode_numpy(encoded_array)
            img = Image.fromarray(frame)
            with io.BytesIO() as buf:
                img.save(buf, format="JPEG")
                im_bytes = buf.getvalue()
                base64_str = base64.b64encode(im_bytes).decode("utf-8")
            # send with websocket
            await websocket.send_text(base64_str)
    except WebSocketDisconnect:
        pass


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


@router.get("", response_model_by_alias=False)
def get_cams(
    id_list: List[schemas.IdString] = Query(None),
) -> List[schemas.Cam]:
    """Retrieve all database cams

    Args:
        id_list (List[schemas.IdString], optional):
        If given only return cams within this list.

    Returns:
        List of cams
    """
    try:
        result = crud.get_cams(id_list=id_list)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.post("", response_model_by_alias=False)
def create_cam(cam: schemas.CamCreate) -> schemas.Cam:
    """Create new cam

    Args:
        cam_id (schemas.IdString): id of the dartboard

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

    Args:
        cam_id (schemas.IdString): id of the dartboard

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

    Args:
        cam_id (schemas.IdString): id of the dartboard

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

    Args:
        cam_id (schemas.IdString): id of the dartboard

    Returns:
        Cam with given id
    """
    try:
        result = crud.get_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    return result


@router.get("/{cam_id}/start")
def start_cam(
    cam_id: schemas.IdString,
) -> schemas.Cam:
    """starts the worker tasks for the cam

    Args:
        cam_id (schemas.IdString): id of the dartboard

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    try:
        cam = crud.get_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e

    # check if cam is active and task still running
    if cam.active:
        r = celery_app.AsyncResult(cam.active_task)
        if r.status == "PENDING":
            return cam
        elif r.status == "FAILURE":
            cam = crud.update_cam(
                cam_id, schemas.CamPatch(active=False, active_task=None)
            )
            raise HTTPException(
                500, "Active task failed. Set cam to inactive. Retry again"
            )
        else:
            cam = crud.update_cam(
                cam_id, schemas.CamPatch(active=False, active_task=None)
            )
    # Start camera
    r = process_camera.delay(cam.hardware_id, cam_id)
    updated_cam = crud.update_cam(
        cam_id, schemas.CamPatch(active=True, active_task=r.id)
    )
    return updated_cam


@router.get("/{cam_id}/stop")
def stop_cam(
    cam_id: schemas.IdString,
) -> schemas.Cam:
    """Will stop all active worker tasks at the moment

    Args:
        cam_id (schemas.IdString): id of the dartboard

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    try:
        cam = crud.get_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e

    if cam.active:
        res = AbortableAsyncResult(cam.active_task, app=celery_app)
        res.abort()
        cam = crud.update_cam(cam_id, schemas.CamPatch(active=False, active_task=None))

    return cam


@router.get("/{cam_id}/frame")
def get_image(
    cam_id: schemas.IdString,
) -> Response:
    """Returns the current frame of the camera

    Args:
        cam_id (schemas.IdString): id of the dartboard
    """
    r = redis.Redis(host="redis", port=6379)
    encoded = r.get(f"img_{cam_id}")
    frame = decode_numpy(encoded)
    img = Image.fromarray(frame)
    with io.BytesIO() as buf:
        img.save(buf, format="PNG")
        im_bytes = buf.getvalue()

    return Response(im_bytes, media_type="image/png")
