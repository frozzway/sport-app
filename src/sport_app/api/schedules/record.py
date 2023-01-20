from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...schemas import ScheduleRecord, ScheduleRecordCreate
from ...services.schedule import ScheduleService


router = APIRouter(
    prefix='/record',
    tags=['Записи расписания']
)


@router.post(
    '/',
    response_model=ScheduleRecord
)
def create_record(
    record_data: ScheduleRecordCreate,
    schedule_service: ScheduleService = Depends()
):
    return schedule_service.create_record(record_data)