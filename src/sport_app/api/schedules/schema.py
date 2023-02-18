from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...models import (
    Schema,
    SchemaCreate,
    SchemaUpdate,
    SchemaRecord
)
from ...services import SchemaService


router = APIRouter(
    prefix='/schema',
    tags=['schedule schemas']
)


@router.post(
    '/',
    response_model=Schema,
    status_code=status.HTTP_201_CREATED,
)
def create_schema(
    schema_data: SchemaCreate,
    schema_service: SchemaService = Depends()
):
    return schema_service.create_schema(schema_data)


@router.get(
    '/',
    response_model=list[Schema]
)
def get_schemas(
    schema_service: SchemaService = Depends()
):
    return schema_service.get_many_schemas()


@router.put(
    '/{schema_id}',
    response_model=Schema
)
def update_schema(
    schema_id: int,
    schema_data: SchemaUpdate,
    schema_service: SchemaService = Depends(),
):
    return schema_service.update_schema(schema_id, schema_data)


@router.delete(
    '/{schema_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_schema(
    schema_id: int,
    schema_service: SchemaService = Depends(),
):
    return schema_service.delete_schema(schema_id)


@router.get(
    '/{schema_id}/records',
    response_model=list[SchemaRecord]
)
def get_records_within_schema(
    schema_id: int,
    schema_service: SchemaService = Depends()
):
    return schema_service.get_schema_records(schema_id)


@router.post(
    '/{schema_id}/records',
    response_model=list[int],
    description='Добавить записи к схеме',
)
def include_records_in_schema(
    schema_id: int,
    records: list[int],
    schema_service: SchemaService = Depends()
):
    return schema_service.include_records_in_schema(schema_id, records)


@router.delete(
    '/{schema_id}/records',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Удалить записи из схемы',
)
def exclude_records_from_schema(
    schema_id: int,
    records: list[int],
    schema_service: SchemaService = Depends()
):
    schema_service.exclude_records_from_schema(schema_id, records)
    return Response(status_code=status.HTTP_204_NO_CONTENT)