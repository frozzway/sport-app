import datetime
import enum

from pydantic import BaseModel
from . import Program


class Periods(str, enum.Enum):
    week = "week"
    month = "month"


class ProgramsReport(BaseModel):
    programs: list[int]
    period: Periods

    class Config:
        use_enum_values = False


class ProgramsReportRow(BaseModel):
    period_begin: datetime.datetime
    period_end: datetime.datetime
    period_num: int
    amount: int


class ClientReportRow(BaseModel):
    program: Program
    data: list[ProgramsReportRow]


class ProgramsReportResponse(ProgramsReport):
    data: list[ProgramsReportRow]