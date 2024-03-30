"""
this module contains functions to perform CRUD operations on dartboard model
"""

from typing import List

from bson import ObjectId

import countdart.database.schemas as schemas
from countdart.database.db import NameAlreadyTakenError, NotFoundError, database

collection = database["Dartboards"]


def get_dartboards() -> List[schemas.Dartboard]:
    """Retrieve all dartboards from database.

    Returns:
        List of dartboards
    """
    result = collection.find()
    return [schemas.Dartboard(**r) for r in result]


def create_dartboard(dartboard: schemas.DartboardCreate) -> schemas.Dartboard:
    """Create a new dartboard from dartboard model and save in database

    Args:
        dartboard: sqlmodel of dartboard to create

    Returns:
        created dartboard
    """
    document = dartboard.model_dump()

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
    document = dartboard.model_dump(exclude_unset=True)
    result = collection.update_one(
        {"_id": ObjectId(dartboard_id)},
        {"$set": document},
    )
    if not result.matched_count:
        raise NotFoundError(f"Dartboard with id {dartboard_id} not found")
    return get_dartboard(dartboard_id)


def delete_dartboard(dartboard_id: schemas.IdString):
    """Delete dartboard with given id from database

    Args:
        dartboard_id: Unique id of dartboard

    Returns:
        string "Deleted"
    """
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
