from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...schemas import Instructor
from ...schemas import InstructorCreate
from ...schemas import InstructorUpdate
from ...services.classes import InstructorService


router = APIRouter(
    prefix='/instructor',
    tags=['Инструктора']
)


@router.get(
    '/{instructor_id}',
    response_model=Instructor
)
def get_instructor(
    instructor_id: int,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.get(instructor_id)


@router.get(
    '/',
    response_model=list[Instructor]
)
def get_instructors(
    instructor_service: InstructorService = Depends()
):
    return instructor_service.get_many()


@router.post(
    '/',
    response_model=Instructor,
    status_code=status.HTTP_201_CREATED,
)
def create_instructor(
    instructor_data: InstructorCreate,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.create(instructor_data)


@router.put(
    '/{instructor_id}',
    response_model=Instructor
)
def update_instructor(
    instructor_id: int,
    instructor_data: InstructorUpdate,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.update(instructor_id, instructor_data)


@router.delete(
    '/{instructor_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_instructor(
    instructor_id: int,
    instructor_service: InstructorService = Depends()
):
    instructor_service.delete(instructor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)