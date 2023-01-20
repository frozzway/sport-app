from fastapi import APIRouter

from . import (
    schema,
    record
)

schedule_router = APIRouter(
    prefix='/schedule'
)
schedule_router.include_router(schema.router)
schedule_router.include_router(record.router)