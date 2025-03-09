"""REST API endpoint for cams.
Used to retrieve, create, update and delete dartboards
"""

import asyncio
import base64
import io
import json
from typing import List, Optional

import numpy as np
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
from countdart.database.crud import dartboard as crud_dartboard
from countdart.database.db import NameAlreadyTakenError, NotFoundError
from countdart.database.schemas.config import AllConfigModel, DeleteConfigModel
from countdart.operators import FrameGrabber, USBCam
from countdart.procedures.base import PROCEDURES
from countdart.settings import settings
from countdart.utils.misc import decode_numpy, remove, update_config_list

router = APIRouter(prefix="/cams", tags=["Camera"])


@router.websocket("/ws/{cam_id}/live")
async def websocket_endpoint(cam_id: schemas.IdString, websocket: WebSocket):
    """Will return websocket, which sends a live stream of given
    camera (cam_id) as a b64 decoded string.
    At default it sends the output of USBCam. To change the output of the live view
    to another operator send a textmessage with the name of the operator.
    Currently "USBCam", "HomographyWarper" and "ChangeDetector" are supported.
    If an image is available it will be send, otherwise it will send
    the string "undefined"

    Args:
        cam_id (schemas.IdString): _description_
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    encoded_array = None
    old_result = None
    # Get cam model
    try:
        cam_db = crud.get_cam(cam_id)
    except NotFoundError as e:
        raise HTTPException(404) from e
    operator = cam_db.type
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    try:
        while True:
            # Add this try block to yield back control to fastapi and allow
            # context switch and serve multiple request concurrently
            # receive_text is also needed to update state of connection:
            # https://github.com/tiangolo/fastapi/discussions/9031#discussion-4911299
            # Important: you need to wait as long as 0.001, otherwise disconnections
            # will not be received, because the wait time is too short
            try:
                operator = await asyncio.wait_for(websocket.receive_text(), 0.001)
            except asyncio.TimeoutError:
                pass

            # Get result from redis
            result = r.get(f"cam_{cam_id}_ResultPublisher")
            if result and result != "" and result != old_result:
                old_result = result
                await websocket.send_text(result.decode())

            # Get Frame from redis
            encoded = r.get(f"cam_{cam_id}_{operator}")
            # check if value changed, otherwise no update needs to be send
            if encoded_array == encoded:
                continue
            else:
                encoded_array = encoded
            # decode numpy array to base64 string
            try:
                frame = decode_numpy(encoded_array)
            except TypeError:
                await websocket.send_text(
                    json.dumps({"type": "error", "content": "could not encode image"})
                )
                continue
            # squeeze array for 2d images
            frame = np.squeeze(frame)
            img = Image.fromarray(frame)
            with io.BytesIO() as buf:
                img.save(buf, format="JPEG")
                im_bytes = buf.getvalue()
                base64_str = base64.b64encode(im_bytes).decode("utf-8")
            # send with websocket
            await websocket.send_text(
                json.dumps({"type": "image", "content": base64_str})
            )
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
        cam (schemas.CamCreate): Cam schema to create

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
        cam_id (schemas.IdString): id of the cam

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
        cam_id (schemas.IdString): id of the cam

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
        cam_id (schemas.IdString): id of the cam

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
    # get dartboard to dynamically create procedure
    dartboard = crud_dartboard.get_dartboards(cam=cam_id)[0]
    algorithm = PROCEDURES.build(dartboard.model_dump())
    # start procedure with cam
    r = algorithm.delay(
        cam.model_dump(), op_configs=dartboard.model_dump()["op_configs"]
    )
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
        cam_id (schemas.IdString): id of the cam
    """
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    encoded = r.get(f"cam_{cam_id}_img_raw")
    frame = decode_numpy(encoded)
    img = Image.fromarray(frame)
    with io.BytesIO() as buf:
        img.save(buf, format="PNG")
        im_bytes = buf.getvalue()

    return Response(im_bytes, media_type="image/png")


@router.get("/{cam_id}/config")
def get_config(
    cam_id: schemas.IdString,
) -> List[AllConfigModel]:
    """Returns config and possible settings about cam.

    Args:
        cam_id (schemas.IdString): id of the cam

    Returns:
        Dict[str, Any]: List with all possible config models
    """
    cam_db = crud.get_cam(cam_id)
    cam = FrameGrabber.build_from_model(cam_db, config=cam_db.cam_config)
    return cam.get_config()


@router.get("/{cam_id}/fps")
def get_cam_fps(
    cam_id: schemas.IdString,
) -> float:
    """Returns current fps of the cam

    Args:
        cam_id (schemas.IdString): id of the cam

    Returns:
        float: fps
    """
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    fps = r.get(f"cam_{cam_id}_FpsCalculator")
    return fps if fps else 0


@router.patch("/{cam_id}/config")
def set_config(cam_id: schemas.IdString, config: List[AllConfigModel]) -> schemas.Cam:
    """Patch camera config.

    Args:
        cam_id (schemas.IdString): id of the cam

    Returns:
        str: returns always "Done"
    """
    # update db entry with cam config
    try:
        old_config = crud.get_cam(cam_id).cam_config
        updated_config = update_config_list(old_config, config)
        patch = schemas.CamPatch(cam_config=updated_config)
        updated = crud.update_cam(cam_id, patch)
        # use redis to apply config to worker processes
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        r.set(
            f"cam_{cam_id}_config",
            json.dumps({updated.type: [c.model_dump() for c in patch.cam_config]}),
        )
    except NotFoundError as e:
        raise HTTPException(404) from e

    return updated


@router.delete("/{cam_id}/config")
def delete_config(cam_id: schemas.IdString, name: Optional[str] = None) -> schemas.Cam:
    """Delete config

    Args:
        cam_id (schemas.IdString): cam id
        name (Optional[str], optional): name of config which should be deleted.
            If not given, deletes all configs. Defaults to None.

    Raises:
        HTTPException: 404 if cam id was not found

    Returns:
        schemas.Cam: updated cam
    """

    # save deleted configs to update live camera
    deletions = []
    try:
        db_cam = crud.get_cam(cam_id)
        old_config = db_cam.cam_config
        # if name given only delete the specified config
        if name:
            updated_config, deleted_config = remove(old_config, "name", name)
            if not deleted_config:
                # Nothing to delete
                return db_cam
            # create delete config model
            deleted_config.type = "_delete_"
            deletions.append(DeleteConfigModel(**deleted_config.model_dump()))
        else:
            # delete all configs
            updated_config = []
            # create delete config model for each existing one
            for deleted_conf in old_config:
                deleted_conf.type = "_delete_"
                deletions.append(DeleteConfigModel(**deleted_conf.model_dump()))
        # update database
        patch = schemas.CamPatch(cam_config=updated_config)
        updated = crud.update_cam(cam_id, patch)
        # use redis to apply config to worker processes
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        r.set(
            f"cam_{cam_id}_config",
            json.dumps({updated.type: [c.model_dump() for c in deletions]}),
        )
    except NotFoundError as e:
        raise HTTPException(404) from e

    return updated
