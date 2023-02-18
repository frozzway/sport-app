from fastapi import APIRouter

from .classes import classes_router
from .schedules import schedule_router
from .clients import router as client_router

router = APIRouter()
router.include_router(classes_router)
router.include_router(schedule_router)
router.include_router(client_router)
