from typing import Optional, Union

from pydantic import (
    BaseModel,
    Field
)
from .classes import Class
import datetime


class ScheduleSchemaBase(BaseModel):
    name: str = Field(max_length=100)
    active: bool


class ScheduleSchemaCreate(BaseModel):
    name: str = Field(max_length=100)
    active: bool = False


class ScheduleSchemaUpdate(BaseModel):
    name: Optional[str] = Field(max_length=100)
    active: Optional[bool]
    activate_next_week: Optional[bool] = False


class ScheduleSchema(ScheduleSchemaBase):
    id: int
    to_be_active_from: datetime.datetime = None

    class Config:
        orm_mode = True


class ScheduleRecordBase(BaseModel):
    week_day: int = Field(ge=0, le=6)
    day_time: datetime.time
    duration: int = Field(ge=5, le=720)


class ScheduleRecordCreate(ScheduleRecordBase):
    Class: Union[Class, int]


class ScheduleRecord(ScheduleRecordBase):
    id: int
    Class: Class

    class Config:
        orm_mode: True


# class ScheduleSchemaRecord(BaseModel):
#     records: list[int]