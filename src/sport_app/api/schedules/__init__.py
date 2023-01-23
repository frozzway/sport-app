from fastapi import APIRouter

from . import (
    schema,
    record,
    schedule
)

schedule_router = APIRouter(
    prefix='/schedule'
)
schedule_router.include_router(schema.router)
schedule_router.include_router(record.router)
schedule_router.include_router(schedule.router)