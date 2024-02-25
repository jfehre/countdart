"""FastAPI Routes and endpoints"""
from fastapi import APIRouter

from .cam import router as cam_router
from .dartboard import router as dartboard_router
from .test import router as test_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(test_router)
router.include_router(dartboard_router)
router.include_router(cam_router)
