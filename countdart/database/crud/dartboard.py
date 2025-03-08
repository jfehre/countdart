"""
this module contains functions to perform CRUD operations on dartboard model
"""

from typing import List

from bson import ObjectId

import countdart.database.schemas as schemas
from countdart.database.crud import cam as cam_crud
from countdart.database.db import NameAlreadyTakenError, NotFoundError, database
from countdart.procedures.base import PROCEDURES

collection = database["Dartboards"]


def get_dartboards(
    id_list: List[schemas.IdString] = None,
    cam: schemas.IdString = None,
    active: bool = None,
) -> List[schemas.Dartboard]:
    """Retrieve all dartboards from database.

    Args:
        id_list: List of ids to return
        cam: Filter all dartboards which contain cam

    Returns:
        List of dartboards
    """
    _filter = {}
    if id_list:
        # Check for empty strings, because frontend may send empty string on purpose
        _filter["_id"] = {
            "$in": [ObjectId(_id) if _id != "" else None for _id in id_list]
        }
    if cam:
        _filter["cams"] = cam
    if active:
        _filter["active"] = active
    result = collection.find(_filter)
    return [schemas.Dartboard(**r) for r in result]


def create_dartboard(dartboard: schemas.DartboardCreate) -> schemas.Dartboard:
    """Create a new dartboard from dartboard model and save in database

    Args:
        dartboard: sqlmodel of dartboard to create

    Returns:
        created dartboard
    """
    document = dartboard.model_dump()
    # Initialize dartboard with default configs
    # from given procedure type
    procedure = PROCEDURES.build(document.copy())
    configs = procedure.get_config()
    encoded_configs = {}
    # encode configs to dicts
    for key, config_list in configs.items():
        if config_list:
            encoded_configs[key] = [c.dict() for c in config_list]
    document["op_configs"] = encoded_configs

    try:
        result = collection.insert_one(document)
    except Exception:
        raise NameAlreadyTakenError(
            f"Dartboard with name {dartboard.name} already exists"
        )
    return get_dartboard(result.inserted_id)


def update_dartboard(
    dartboard_id: schemas.IdString,
    dartboard: schemas.DartboardPatch,
) -> schemas.Dartboard:
    """Update dartboard, is given existing dartboard and modified dartboard

    Args:
        dartboard: existing dartboard
        modified_dartboard: modified dartboard model

    Returns:
        updated dartboard
    """
    # TODO: update config
    document = dartboard.model_dump(exclude_unset=True)
    result = collection.update_one(
        {"_id": ObjectId(dartboard_id)},
        {"$set": document},
    )
    if not result.matched_count:
        raise NotFoundError(f"Dartboard with id {dartboard_id} not found")
    return get_dartboard(dartboard_id)


def delete_dartboard(dartboard_id: schemas.IdString):
    """Delete dartboard with given id from database.
    Will also delete associated cams.

    Args:
        dartboard_id: Unique id of dartboard

    Returns:
        string "Deleted"
    """
    # delete dartboard
    dartboard = get_dartboard(dartboard_id)
    for cam in dartboard.cams:
        cam_crud.delete_cam(cam)
    result = collection.delete_one({"_id": ObjectId(dartboard_id)})
    if not result.deleted_count:
        raise NotFoundError(f"Dartboard with id {dartboard_id} not found")


def get_dartboard(dartboard_id: schemas.IdString) -> schemas.Dartboard:
    """Retrieve specific Dartboard with given id from database

    Args:
        dartboard_id: Unique id of dartboard
        session: SQL session

    Returns:
        Dartboard with given id
    """
    result = collection.find_one({"_id": ObjectId(dartboard_id)})
    if result is None:
        raise NotFoundError(f"Dartboard with id {dartboard_id} not found")
    return schemas.Dartboard(**result)
