"""
FastAPI Routes and endpoints
"""
from fastapi import APIRouter

from .test import router as test_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(test_router)
