from fastapi import APIRouter

from .programs import programs_router
from .schedules import schedule_router
from .clients import router as client_router
from .auth import router as auth_router
from .reports import router as report_router

router = APIRouter(
    prefix='/api'
)
router.include_router(programs_router)
router.include_router(schedule_router)
router.include_router(client_router)
router.include_router(auth_router)
router.include_router(report_router)
