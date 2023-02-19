from fastapi import (
    APIRouter,
    Depends
)
from typing import Optional

from ...models import ScheduleRecord
from ...services import ScheduleService


router = APIRouter(
    tags=['schedule'],
)


@router.get(
    '/',
    response_model=list[ScheduleRecord]
)
def get_schedule(
    category: Optional[str] = None,
    instructor: Optional[int] = None,
    placement: Optional[str] = None,
    program: Optional[int] = None,
    schedule_service: ScheduleService = Depends()
):
    filters = {
        "category": category,
        "instructor": instructor,
        "placement": placement,
        "id": program,
    }
    return schedule_service.construct_schedule(filters)