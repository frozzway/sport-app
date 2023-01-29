from fastapi import (
    APIRouter,
    Depends
)

from ...models import SchemaRecord, SchemaRecordCreate
from ...services import RecordService


router = APIRouter(
    prefix='/record',
    tags=['Записи расписания']
)


@router.post(
    '/',
    response_model=SchemaRecord
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