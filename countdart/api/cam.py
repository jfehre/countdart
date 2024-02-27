import io
import struct
from typing import List

import numpy as np
import redis
from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response
from PIL import Image
from sqlmodel import Session

from countdart.celery_app import celery_app
from countdart.database import get_session, schemas
from countdart.database.crud import cam as crud
from countdart.io import USBCam
from countdart.worker import process_camera

router = APIRouter(prefix="/cams", tags=["Camera"])


@router.post("", response_model=schemas.CamRead)
def create_cam(
    cam: schemas.CamCreate, session: Session = Depends(get_session)
) -> schemas.CamRead:
    """Create new cam

    Returns:
        Created cam
    """
    cam = crud.create_cam(cam, session)
    return cam


@router.get("", response_model=List[schemas.CamRead])
def get_cams(session: Session = Depends(get_session)):
    """Retrieve all database cams

    Returns:
        List of cams
    """
    cams = crud.get_cams(session)
    return cams


@router.get("/find", response_model=List[schemas.CamHardware])
def find_cams():
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


@router.get("/{cam_id}", response_model=schemas.CamRead)
def get_cam(cam_id: int, session: Session = Depends(get_session)):
    """Retrieve cam with given id

    Returns:
        Cam with given id
    """
    cam = crud.get_cam(cam_id, session)

    if cam is None:
        raise HTTPException(status_code=404, detail=f"Cam with id={cam_id} not found")
    return cam


@router.patch("/{cam_id}", response_model=schemas.CamRead)
def update_cam(
    cam_id: int,
    cam: schemas.CamPatch,
    session: Session = Depends(get_session),
):
    """Retrieve cam with given id

    Returns:
        cam with given id
    """
    # retrieve existing dartboard
    db_cam = crud.get_cam(cam_id, session)
    if cam is None:
        raise HTTPException(status_code=404, detail=f"Cam with id={cam_id} not found")
    updated = crud.update_cam(db_cam, cam, session)
    return updated


@router.delete("/{cam_id}", response_model=schemas.CamRead)
def delete_cam(
    cam_id: int,
    session: Session = Depends(get_session),
):
    """Delete cam with given id

    Returns:
        cam with given id
    """
    cam = crud.delete_cam(cam_id, session)
    if cam is None:
        raise HTTPException(status_code=404, detail=f"Cam with id={cam_id} not found")
    return cam


@router.get("/{cam_id}/start", response_model=schemas.TaskOut)
def start_cam(
    cam_id: int,
    session: Session = Depends(get_session),
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
    session: Session = Depends(get_session),
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


@router.get("/{cam_id}/frame", response_class=Response)
def get_image(
    cam_id: int,
):
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
