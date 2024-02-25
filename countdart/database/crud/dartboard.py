"""
this module contains functions to perform CRUD operations on dartboard model
"""

from typing import List

from sqlalchemy.orm import Session

import countdart.database.schemas as schemas


def get_dartboards(session: Session) -> List[schemas.Dartboard]:
    """Retrieve all dartboards from database.

    Args:
        session: SQL session

    Returns:
        List of dartboards
    """
    dartboards = session.query(schemas.Dartboard).all()
    return dartboards


def get_dartboard(dartboard_id: int, session: Session) -> schemas.Dartboard:
    """Retrieve specific Dartboard with given id from database

    Args:
        dartboard_id: Unique id of dartboard
        session: SQL session

    Returns:
        Dartboard with given id
    """
    dartboard = (
        session.query(schemas.Dartboard)
        .filter(schemas.Dartboard.id == dartboard_id)
        .first()
    )
    return dartboard


def create_dartboard(
    dartboard: schemas.DartboardCreate, session: Session
) -> schemas.DartboardRead:
    """Create a new dartboard from dartboard model and save in database

    Args:
        dartboard: sqlmodel of dartboard to create
        session: SQL session

    Returns:
        created dartboard
    """
    db_is = schemas.Dartboard.model_validate(dartboard)
    session.add(db_is)
    session.commit()
    session.refresh(db_is)
    return db_is


def update_dartboard(
    existing_dartboard: schemas.Dartboard,
    modified_dartboard: schemas.DartboardPatch,
    session: Session,
) -> schemas.Dartboard:
    """Update dartboard, is given existing dartboard and modified dartboard

    Args:
        dartboard: existing dartboard
        modified_dartboard: modified dartboard model
        session: SQL session

    Returns:
        updated dartboard
    """
    updated_data = modified_dartboard.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(existing_dartboard, key, value) if value is not None else None
    session.commit()
    session.refresh(existing_dartboard)
    return existing_dartboard


def delete_dartboard(dartboard_id: int, session: Session):
    """Delete dartboard with given id from database

    Args:
        dartboard_id: Unique id of dartboard
        session: SQL session

    Returns:
        string "Deleted"
    """
    dartboard = get_dartboard(dartboard_id, session)
    session.delete(dartboard)
    session.commit()
    return dartboard
