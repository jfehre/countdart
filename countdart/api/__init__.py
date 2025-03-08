"""FastAPI Routes and endpoints"""
from typing import Dict

from fastapi import APIRouter

from .cam import router as cam_router
from .dartboard import router as dartboard_router
from .games import router as game_router
from .test import router as test_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(test_router)
router.include_router(dartboard_router)
router.include_router(cam_router)
router.include_router(game_router)


@router.get("/health")
def health() -> Dict[str, str]:
    """Health check if api is running

    Returns:
        Dict[str, str]: {"status": "ok"}
    """
    return {"status": "ok"}
