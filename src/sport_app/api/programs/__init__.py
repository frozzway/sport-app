from fastapi import APIRouter

from . import (
    category,
    placement,
    instructor,
    program
)

programs_router = APIRouter(
    prefix='/programs'
)
programs_router.include_router(category.router)
programs_router.include_router(placement.router)
programs_router.include_router(instructor.router)
programs_router.include_router(program.router)