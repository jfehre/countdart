"""REST API endpoint for dartboards.
Used to retrieve, create, update and delete dartboards
"""

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
from countdart.database.crud import dartboard as crud
from countdart.worker import process_camera

router = APIRouter(prefix="/dartboard", tags=["dartboard"])


@router.post("", response_model=List[schemas.DartboardRead])
def create_dartboard(
    dartboard: schemas.DartboardCreate, session: Session = Depends(get_session)
) -> schemas.DartboardRead:
    """Create new dartboard

    Returns:
        Created dartboard
    """
    dartboard = crud.create_dartboard(dartboard, session)
    return dartboard


@router.get("", response_model=List[schemas.DartboardRead])
def get_dartboards(session: Session = Depends(get_session)):
    """Retrieve all dartboards

    Returns:
        List of dartboards
    """
    dartboards = crud.get_dartboards(session)
    return dartboards


@router.get("/{dartboard_id}", response_model=schemas.DartboardRead)
def get_dartboard(dartboard_id: int, session: Session = Depends(get_session)):
    """Retrieve dartboard with given id

    Returns:
        Dartboard with given id
    """
    dartboard = crud.get_dartboard(dartboard_id, session)

    if dartboard is None:
        raise HTTPException(
            status_code=404, detail=f"Dartboard with id={dartboard_id} not found"
        )
    return dartboard


@router.patch("/{dartboard_id}", response_model=schemas.DartboardRead)
def update_dartboard(
    dartboard_id: int,
    dartboard: schemas.DartboardPatch,
    session: Session = Depends(get_session),
):
    """Retrieve dartboard with given id

    Returns:
        Dartboard with given id
    """
    # retrieve existing dartboard
    db_dartboard = crud.get_dartboard(dartboard_id, session)
    if dartboard is None:
        raise HTTPException(
            status_code=404, detail=f"Dartboard with id={dartboard_id} not found"
        )
    updated = crud.update_dartboard(db_dartboard, dartboard, session)
    return updated


@router.get("/{dartboard_id}/start", response_model=schemas.TaskOut)
def start_dartboard(
    dartboard_id: int,
    session: Session = Depends(get_session),
) -> schemas.TaskOut:
    """starts the worker tasks for the dartboard

    Args:
        session (Session, optional): sql session. Defaults to Depends(get_session).

    Returns:
        schemas.TaskOut: Information about the started Task
    """
    r = process_camera.delay(0)
    return schemas.TaskOut.celery_to_task_out(r)


@router.get("/{dartboard_id}/stop")
def stop_dartboard(
    dartboard_id: int,
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


@router.get("/{dartboard_id}/frame", response_class=Response)
def get_image(
    dartboard_id: int,
):
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
