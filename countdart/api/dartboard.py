"""
REST API endpoint for dartboards.
Used to retrieve, create, update and delete dartboards
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from countdart.database import get_session, schemas
from countdart.database.crud import dartboard as crud

router = APIRouter(prefix="/dartboard", tags=["dartboard"])


@router.post("", response_model=List[schemas.DartboardRead])
def create_dartboard(
    dartboard: schemas.DartboardCreate, session: Session = Depends(get_session)
) -> schemas.DartboardRead:
    """Create new dartboard

    :return: Created dartboard
    """
    dartboard = crud.create_dartboard(dartboard, session)
    return dartboard


@router.get("", response_model=List[schemas.DartboardRead])
def get_dartboards(session: Session = Depends(get_session)):
    """Retrieve all dartboards

    :return: List of dartboards
    """
    dartboards = crud.get_dartboards(session)
    return dartboards


@router.get("/{dartboard_id}", response_model=schemas.DartboardRead)
def get_dartboard(dartboard_id: int, session: Session = Depends(get_session)):
    """Retrieve dartboard with given id

    :return: Dartboard with given id
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

    :return: Dartboard with given id
    """
    # retrieve existing dartboard
    db_dartboard = crud.get_dartboard(dartboard_id, session)
    if dartboard is None:
        raise HTTPException(
            status_code=404, detail=f"Dartboard with id={dartboard_id} not found"
        )
    updated = crud.update_dartboard(db_dartboard, dartboard, session)
    return updated
