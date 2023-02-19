from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...models import SchemaRecord, SchemaRecordCreate
from ...services import RecordService
from ...services.auth import validate_admin_access


router = APIRouter(
    prefix='/record',
    tags=['records'],
    dependencies=[Depends(validate_admin_access)],
)


@router.post(
    '/',
    response_model=SchemaRecord,
    status_code=status.HTTP_201_CREATED,
)
def create_record(
    record_data: SchemaRecordCreate,
    record_service: RecordService = Depends()
):
    return record_service.create_record(record_data)


@router.get(
    '/',
    response_model=list[SchemaRecord]
)
def get_records(
    record_service: RecordService = Depends()
):
    return record_service.get_many()


@router.delete(
    '/{record_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_record(
    record_id: int,
    record_service: RecordService = Depends()
):
    record_service.delete_record(record_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)