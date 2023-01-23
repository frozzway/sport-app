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


class ScheduleRow(NamedTuple):
    Class: tables.Class
    SchemaRecord: tables.SchemaRecord
    booked_places: Optional[int] = None

    def to_schema(self) -> schemas.ScheduleRecord:
        class_, record, booked_places = self.Class, self.SchemaRecord, self.booked_places
        place_limit = class_.place_limit
        places_available = None
        registration_opens_at = None

        if class_.registration_opens and record.date >= utils.today():
            if place_limit:
                places_available = place_limit - booked_places
            pre_days = rd.relativedelta(days=class_.registration_opens, hour=16)  # days before registration opens
            registration_opens_at = record.date - pre_days

        return schemas.ScheduleRecord(
                Class=schemas.ScheduleClass(
                    **class_.to_schema().dict(),
                    places_available=places_available,
                    registration_opens_at=registration_opens_at
                ),
                date=record.date
            )

    def __eq__(self, other):
        if self.Class.id == other.Class.id and self.SchemaRecord.date == self.SchemaRecord.date:
            return True
        return False


class GridRow(NamedTuple):
    Class: tables.Class
    SchemaRecord: tables.SchemaRecord


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

    def _get_schedule(
        self,
        schema: tables.ScheduleSchema,
        next_week: bool = False
    ) -> list[schemas.ScheduleRecord]:
        BC, SSR = alias(tables.BookedClasses), alias(tables.schedule_schema_record)
        class_date = utils.calc_date_sql(tables.SchemaRecord.week_day, tables.SchemaRecord.day_time)
        if next_week:
            class_date += 7
        stmt = (
            select(tables.Class, tables.SchemaRecord, func.count(BC.c.id))
            .join(tables.SchemaRecord)
            .join(BC, isouter=True)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
            .where(
                and_(
                    (BC.c.date == utils.tz_date_sql(class_date)),
                    BC.c.date > utils.this_mo_sql()
                ) | BC.c.date.is_(None)
            )
            .group_by(tables.Class, tables.SchemaRecord)
        )
        rows = self.session.execute(stmt).all()
        return [(ScheduleRow(Class=row.Class,
                             SchemaRecord=row.SchemaRecord,
                             booked_places=row.count)).to_schema()
                for row in rows]

    def _get_schedule_grid(self, schema: tables.ScheduleSchema):
        SSR = alias(tables.schedule_schema_record)
        stmt = (
            select(tables.Class, tables.SchemaRecord)
            .join(tables.SchemaRecord)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
        )
        grid = [ScheduleRow(row[0], row[1]) for row in self.session.execute(stmt).all()]
        classes_with_registration = [r for r in grid if r.Class.available_registration]
        classes_without_registration = [r for r in grid if r.Class.available_registration is False]
        counted_classes = self._count_booked_classes(schema)

    def _count_booked_classes(
        self,
        schema: tables.ScheduleSchema
    ) -> list[ScheduleRow]:
        """Возвращает те занятия (<class.id, bc.c.date>: count), на которые записывались клиенты (с подсчетом кол-ва записавшихся).
           Возвращает те занятия, на которые открыта запись, но никто еще не записался.
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
                (
                    or_(
                        BC.c.date == utils.tz_date_sql(class_date),
                        BC.c.date == utils.tz_date_sql(class_date + 7)
                    ) & BC.c.date > func.now()
                ) | BC.c.date.is_(None)
            )
            .group_by(tables.Class, tables.SchemaRecord, BC.c.date)
        )
        rows = self.session.execute(stmt).all()
        return [(ScheduleRow(Class=row.Class,
                             SchemaRecord=row.SchemaRecord,
                             booked_places=row.count))
                for row in rows]

    def construct_schedule(self) -> list[schemas.ScheduleRecord]:
        self._validate_active_schema()
        active_schema = self.schema_service.active_schema
        next_week_schema = self.schema_service.next_week_schema or active_schema
        records = self._get_schedule(active_schema)
        next_week_records = self._get_schedule(next_week_schema, next_week=True)
        week = rd.relativedelta(days=7)
        for r in next_week_records:
            r.Class.registration_opens_at += week
            r.date += week

        return records + next_week_records
