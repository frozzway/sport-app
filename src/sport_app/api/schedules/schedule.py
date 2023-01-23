from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...schemas import ScheduleRecord
from ...services.schedule import ScheduleService


router = APIRouter(
    tags=['Расписание']
)


@router.get(
    '/',
    response_model=list[ScheduleRecord]
)
def get_schedule(
    schedule_service: ScheduleService = Depends()
):
    return schedule_service.construct_schedule()