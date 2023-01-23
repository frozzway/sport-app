import datetime
from typing import (
    Optional,
    NamedTuple
)
from copy import deepcopy
from dateutil import relativedelta as rd
from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, func
from sqlalchemy.sql import alias, or_, and_

from .schema import SchemaService
from ..database import get_session
from .. import (
    tables,
    schemas,
    utils
)

ScheduleList = list[schemas.ScheduleRecord]
ScheduleClass = tuple[int, datetime.datetime]
ScheduleDict = dict[ScheduleClass, schemas.ScheduleRecord]


class ScheduleRow(NamedTuple):
    Class: tables.Class
    SchemaRecord: tables.SchemaRecord
    date: Optional[datetime.datetime] = None
    booked_places: Optional[int] = 0

    def to_schema(self) -> schemas.ScheduleRecord:
        class_, record, booked_places = self.Class, self.SchemaRecord, self.booked_places
        date = self.date or self.SchemaRecord.date
        place_limit = class_.place_limit
        places_available = None
        registration_opens_at = None

        if class_.registration_opens and date >= utils.today():
            if place_limit:
                places_available = place_limit - booked_places
            pre_days = rd.relativedelta(days=class_.registration_opens, hour=16)  # days before registration opens
            registration_opens_at = date - pre_days

        return schemas.ScheduleRecord(
                Class=schemas.ScheduleClass(
                    **class_.to_schema().dict(),
                    places_available=places_available,
                    registration_opens_at=registration_opens_at
                ),
                date=date
            )

    def __eq__(self, other):
        return self.Class.id == other.Class.id and self.SchemaRecord.date == self.SchemaRecord.date


class ScheduleService:
    def __init__(
        self,
        session: Session = Depends(get_session),
        schema_service: SchemaService = Depends()
    ):
        self.session = session
        self.schema_service = schema_service

    def _validate_active_schema(self):
        pass

    def _get_grid(self, schema: tables.ScheduleSchema) -> ScheduleDict:
        SSR = alias(tables.schedule_schema_record)
        stmt = (
            select(tables.Class, tables.SchemaRecord)
            .join(tables.SchemaRecord)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
        )
        grid = dict()
        for row in self.session.execute(stmt).all():
            schedule_class: ScheduleClass = (row[0].id, row[1].date)
            schedule_record: schemas.ScheduleRecord = ScheduleRow(row[0], row[1]).to_schema()
            grid[schedule_class] = schedule_record
        return grid

    @staticmethod
    def _prolong_grid(grid: ScheduleDict):
        week = rd.relativedelta(days=7)
        nw_grid = {}
        for k, value in grid.items():
            schedule_class: ScheduleClass = (k[0], k[1] + week)
            schedule_record: schemas.ScheduleRecord = deepcopy(value)
            schedule_record.Class.registration_opens_at += week
            schedule_record.date += week
            nw_grid[schedule_class] = schedule_record
        grid.update(nw_grid)

    def _count_booked_classes(
        self,
        schema: tables.ScheduleSchema
    ) -> ScheduleDict:
        """Возвращает те занятия, на которые записывались клиенты (с подсчетом кол-ва записавшихся).
           Возвращает те занятия, на которые открыта запись и никто еще не записался.
           Начиная с now()
        """
        BC, SSR = alias(tables.BookedClasses), alias(tables.schedule_schema_record)
        class_date = utils.calc_date_sql(tables.SchemaRecord.week_day, tables.SchemaRecord.day_time)
        stmt = (
            select(tables.Class, tables.SchemaRecord, BC.c.date, func.count(BC.c.id))
            .join(tables.SchemaRecord)
            .join(BC, isouter=True)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
            .where(tables.Class.available_registration.is_(True))
            .where(
                    or_(
                        BC.c.date == utils.tz_date_sql(class_date),
                        BC.c.date == utils.tz_date_sql(class_date + 7)
                    ) & (BC.c.date > func.now())
            )
            .group_by(tables.Class, tables.SchemaRecord, BC.c.date)
        )
        res = dict()
        for row in self.session.execute(stmt).all():
            schedule_class = (row.Class.id, row.date)
            schedule_record = ScheduleRow(
                Class=row.Class,
                SchemaRecord=row.SchemaRecord,
                date=row.date,
                booked_places=row.count,
            ).to_schema()
            res[schedule_class] = schedule_record
        return res

    def construct_schedule(self) -> ScheduleList:
        self._validate_active_schema()
        active_schema = self.schema_service.active_schema
        next_week_schema = self.schema_service.next_week_schema

        response: ScheduleDict = dict()

        grid = self._get_grid(active_schema)  # записи на этой неделе (без подсчета кол-ва записавшихся)
        counted_classes = self._count_booked_classes(active_schema)

        if not next_week_schema:
            self._prolong_grid(grid)  # добавить такие же записи на след. неделе

        response.update(grid)
        response.update(counted_classes)

        if next_week_schema:
            grid = self._get_grid(next_week_schema)
            response.update(grid)
            counted_classes = self._count_booked_classes(next_week_schema)
            response.update(counted_classes)

        return [r for r in response.values()]
