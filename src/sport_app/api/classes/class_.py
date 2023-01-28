from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...schemas import Class, CreateClass
from ...services import ClassService


router = APIRouter(
    prefix='/class',
    tags=['Занятия']
)


@router.get(
    '/{class_id}',
    response_model=Class
)
def get_class(
    class_id: int,
    class_service: ClassService = Depends()
):
    return class_service.get(class_id)


@router.get(
    '/',
    response_model=list[Class]
)
def get_all_classes(
    class_service: ClassService = Depends()
):
    return class_service.get_many()


@router.post(
    '/',
    response_model=Class,
    status_code=status.HTTP_201_CREATED,
)
def create_class(
    class_data: CreateClass,
    class_service: ClassService = Depends()
):
    return class_service.create_class(class_data)
