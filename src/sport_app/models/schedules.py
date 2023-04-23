from typing import Optional, Union

from pydantic import (
    BaseModel,
    Field
)
from .programs import Program
import datetime


class SchemaBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SchemaCreate(SchemaBase):
    base_schema: Optional[int] = None


class SchemaUpdate(BaseModel):
    name: Optional[str] = Field(max_length=100)
    active: Optional[bool] = None
    activate_next_week: Optional[bool]


class Schema(SchemaBase):
    id: int
    active: bool
    to_be_active_from: datetime.datetime = None

    class Config:
        orm_mode = True


class SchemaRecordBase(BaseModel):
    week_day: int = Field(ge=0, le=6)
    day_time: datetime.time
    duration: int = Field(ge=5, le=720)


class SchemaRecordCreate(SchemaRecordBase):
    program: int


class SchemaRecord(SchemaRecordBase):
    id: int
    program: Program

    class Config:
        orm_mode: True


class ScheduleRecord(BaseModel):
    program: Program
    date: datetime.datetime
    duration: int
    registration_opens_at: Optional[datetime.datetime]
    places_available: Optional[int]