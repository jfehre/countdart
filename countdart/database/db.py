"""
Initializes a postgresql table and contains a factory function
to return sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

POSTGRES_URI = "postgresql://postgres:@db.local:5432/countdart_dev"

__all__ = "get_session"

# Create sql engine to connect with mongodb
engine = create_engine(
    POSTGRES_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(db: Session) -> None:
    """
    Initialize a new database with defined sqlmodel
    """
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    """Creates and returns a sqlalchemy database session

    :yield: _description_
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
