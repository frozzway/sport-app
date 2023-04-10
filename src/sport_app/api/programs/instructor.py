from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile
)

from ...models import (
    Instructor,
    InstructorCreate,
    InstructorUpdate,
    InstructorPublic,
)
from ...services import InstructorService
from ...services.auth import validate_admin_access


router = APIRouter(
    prefix='/instructor',
    tags=['instructors'],
)


@router.get(
    '/{instructor_id}/image',
    response_model=InstructorPublic
)
def get_instructor_image(
    instructor_id: int,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.get_instructor(instructor_id, for_public=True)


@router.get(
    '/{instructor_id}',
    response_model=Instructor,
    dependencies=[Depends(validate_admin_access)],
)
def get_instructor(
    instructor_id: int,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.get_instructor(instructor_id)


@router.get(
    '/',
    response_model=list[Instructor],
    dependencies=[Depends(validate_admin_access)],
)
def get_instructors(
    instructor_service: InstructorService = Depends()
):
    return instructor_service.get_many()


@router.post(
    '/',
    response_model=Instructor,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_admin_access)],
)
def create_instructor(
    instructor_data: InstructorCreate,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.create_instructor(instructor_data)


@router.put(
    '/{instructor_id}',
    response_model=Instructor,
    dependencies=[Depends(validate_admin_access)],
)
def update_instructor(
    instructor_id: int,
    instructor_data: InstructorUpdate,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.update_instructor(instructor_id, instructor_data)


@router.put(
    '/{instructor_id}/image',
    response_model=InstructorPublic,
    dependencies=[Depends(validate_admin_access)],
)
def upload_instructor_image(
    instructor_id: int,
    image: UploadFile,
    instructor_service: InstructorService = Depends()
):
    return instructor_service.upload_image(instructor_id, image)


@router.delete(
    '/{instructor_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_admin_access)],
)
def delete_instructor(
    instructor_id: int,
    instructor_service: InstructorService = Depends()
):
    instructor_service.delete_instructor(instructor_id)
