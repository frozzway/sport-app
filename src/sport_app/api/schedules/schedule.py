from fastapi import (
    APIRouter,
    Depends
)

from ...schemas import ScheduleRecord
from ...services import ScheduleService


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