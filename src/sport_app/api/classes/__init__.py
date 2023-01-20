from fastapi import APIRouter

from . import (
    category,
    placement,
    instructor,
    class_
)

classes_router = APIRouter(
    prefix='/classes'
)
classes_router.include_router(category.router)
classes_router.include_router(placement.router)
classes_router.include_router(instructor.router)
classes_router.include_router(class_.router)