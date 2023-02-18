from fastapi import APIRouter

from . import (
    category,
    placement,
    instructor,
    program
)

classes_router = APIRouter(
    prefix='/programs'
)
classes_router.include_router(category.router)
classes_router.include_router(placement.router)
classes_router.include_router(instructor.router)
classes_router.include_router(program.router)