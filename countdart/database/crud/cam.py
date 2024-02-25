"""
CRUD operations for cam model
"""

from typing import List

from sqlalchemy.orm import Session

import countdart.database.schemas as schemas


def get_cams(session: Session) -> List[schemas.Cam]:
    """
    Retrieve all cams from the database.

    Args:
        session: SQL session

    Returns:
        List of cams
    """
    cams = session.query(schemas.Cam).all()
    return cams


def get_cam(cam_id: int, session: Session) -> schemas.Cam:
    """Retrieve specific cam with given id from database

    Args:
        cam_id: Unique id of cam
        session: SQL session

    Returns:
        cam with given id
    """
    cam = session.query(schemas.Cam).filter(schemas.Cam.id == cam_id).first()
    return cam


def create_cam(cam: schemas.CamCreate, session: Session) -> schemas.Cam:
    """Create a new cam from cam model and save in database

    Args:
        cam: sqlmodel of cam to create
        session: SQL session

    Returns:
        created cam
    """
    db_is = schemas.Cam.model_validate(cam)
    session.add(db_is)
    session.commit()
    session.refresh(db_is)
    return db_is


def update_cam(
    existing_cam: schemas.Cam,
    modified_cam: schemas.CamPatch,
    session: Session,
) -> schemas.Cam:
    """Update cam, is given existing cam and modified cam

    Args:
        cam: existing cam
        modified_cam: modified cam model
        session: SQL session

    Returns:
        updated cam
    """
    updated_data = modified_cam.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(existing_cam, key, value) if value is not None else None
    session.commit()
    session.refresh(existing_cam)
    return existing_cam


def delete_cam(cam_id: int, session: Session):
    """Delete cam with given id from database

    Args:
        cam_id: Unique id of cam
        session: SQL session

    Returns:
        string "Deleted"
    """
    cam = get_cam(cam_id, session)
    session.delete(cam)
    session.commit()
    return cam
