"""
CRUD operations for cam model
"""

from typing import List

from bson import ObjectId

import countdart.database.schemas as schemas
from countdart.database.db import NameAlreadyTakenError, NotFoundError, database

collection = database["cams"]


def get_cams(id_list: List[schemas.IdString] = None) -> List[schemas.Cam]:
    """
    Retrieve all cams from the database.

    Args:
        id_list: List of ids to return

    Returns:
        List of cams
    """
    _filter = {}
    if id_list is not None:
        # Check for empty strings, because frontend will send empty string on purpose
        _filter = {
            "_id": {"$in": [ObjectId(_id) if _id != "" else None for _id in id_list]}
        }
    result = collection.find(_filter)
    return [schemas.Cam(**r) for r in result]


def create_cam(cam: schemas.CamCreate) -> schemas.Cam:
    """Create a new cam from cam model and save in database

    Args:
        cam: model of cam to create

    Returns:
        created cam
    """
    document = cam.model_dump()

    try:
        result = collection.insert_one(document)
    except Exception:
        raise NameAlreadyTakenError(f"Cam with name {cam.name} already exists")
    return get_cam(result.inserted_id)


def update_cam(
    cam_id: schemas.IdString,
    cam: schemas.CamPatch,
) -> schemas.Cam:
    """Update cam, is given existing cam and modified cam

    Args:
        cam: existing cam
        modified_cam: modified cam model

    Returns:
        updated cam
    """
    document = cam.model_dump(exclude_unset=True)
    result = collection.update_one(
        {"_id": ObjectId(cam_id)},
        {"$set": document},
    )
    if not result.matched_count:
        raise NotFoundError(f"Cam with id {cam_id} not found")
    return get_cam(cam_id)


def delete_cam(cam_id: schemas.IdString):
    """Delete cam with given id from database

    Args:
        cam_id: Unique id of cam

    Returns:
        string "Deleted"
    """
    result = collection.delete_one({"_id": ObjectId(cam_id)})
    if not result.deleted_count:
        raise NotFoundError(f"Cam with id {cam_id} not found")


def get_cam(cam_id: schemas.IdString) -> schemas.Cam:
    """Retrieve specific cam with given id from database

    Args:
        cam_id: Unique id of cam

    Returns:
        cam with given id
    """
    result = collection.find_one({"_id": ObjectId(cam_id)})
    if result is None:
        raise NotFoundError(f"Cam with id {cam_id} not found")
    return schemas.Cam(**result)
