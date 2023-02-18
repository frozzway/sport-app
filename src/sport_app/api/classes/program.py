from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...models import Program, CreateProgram
from ...services import ProgramService


router = APIRouter(
    tags=['programs']
)


@router.get(
    '/{program_id}',
    response_model=Program
)
def get_program(
    program_id: int,
    program_service: ProgramService = Depends()
):
    return program_service.get(program_id).to_model()


@router.get(
    '/',
    response_model=list[Program]
)
def get_all_programs(
    program_service: ProgramService = Depends()
):
    return program_service.get_many()


@router.post(
    '/',
    response_model=Program,
    status_code=status.HTTP_201_CREATED,
)
def create_program(
    program_data: CreateProgram,
    program_service: ProgramService = Depends()
):
    return program_service.create_program(program_data)


@router.delete(
    '/{program_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_program(
    program_id: int,
    program_service: ProgramService = Depends()
):
    return program_service.delete_program(program_id)
