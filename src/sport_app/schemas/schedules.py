from typing import Optional, Union

from pydantic import (
    BaseModel,
    Field
)
from .classes import Class
import datetime


class SchemaBase(BaseModel):
    name: str = Field(max_length=100)
    active: bool


class SchemaCreate(BaseModel):
    name: str = Field(max_length=100)
    active: bool = False


class SchemaUpdate(BaseModel):
    name: Optional[str] = Field(max_length=100)
    active: Optional[bool]
    activate_next_week: Optional[bool] = False


class Schema(SchemaBase):
    id: int
    to_be_active_from: datetime.datetime = None

    class Config:
        orm_mode = True


class SchemaRecordBase(BaseModel):
    week_day: int = Field(ge=0, le=6)
    day_time: datetime.time
    duration: int = Field(ge=5, le=720)


class SchemaRecordCreate(SchemaRecordBase):
    Class: Union[Class, int]


class SchemaRecord(SchemaRecordBase):
    id: int
    Class: Class

    class Config:
        orm_mode: True


class ScheduleClass(Class):
    registration_opens_at: Optional[datetime.datetime]
    places_available: Optional[int]


class ScheduleRecord(BaseModel):
    Class: ScheduleClass
    date: datetime.datetime