"""FastAPI Routes and endpoints"""
from fastapi import APIRouter

from .dartboard import router as dartboard_router
from .test import router as test_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(test_router)
router.include_router(dartboard_router)
