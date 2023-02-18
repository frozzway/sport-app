import datetime
from typing import (
    Optional,
    NamedTuple
)

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
from sqlalchemy.sql.expression import Select

from .schema import SchemaService
from sport_app.database import get_session
from sport_app import (
    tables,
    models,
    utils
)


class ScheduleInstance(NamedTuple):
    program: tables.Program
    date: datetime.datetime
    booked_places: Optional[int] = 0

    def __eq__(self, other):
        return all([
            isinstance(other, ScheduleInstance),
            self.program.id == other.program.id,
            self.date == other.date
        ])

    def __hash__(self):
        return hash((self.program.id, self.date))

    def to_schema(self) -> models.ScheduleRecord:
        place_limit = self.program.place_limit
        places_available = None
        registration_opens_at = None

        if self.program.available_registration and self.date >= utils.today():
            if place_limit:
                places_available = place_limit - self.booked_places
            if self.program.registration_opens:
                pre_days = rd.relativedelta(days=self.program.registration_opens, hour=16)  # дней до открытия регистрации
                registration_opens_at = self.date - pre_days

        return models.ScheduleRecord(
                program=self.program.to_model(),
                places_available=places_available,
                registration_opens_at=registration_opens_at,
                date=self.date,
            )


ScheduleSet = set[ScheduleInstance]


class ScheduleService:
    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        self.session = session
        self.schema_service = SchemaService(session)

    def _validate_active_schema(self):
        pass

    def _get_grid(
        self,
        schema: tables.ScheduleSchema,
        filters
    ) -> ScheduleSet:
        SSR = tables.schedule_schema_record
        stmt = self._apply_filters((
            select(tables.Program, tables.SchemaRecord)
            .join(tables.SchemaRecord)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
        ), filters)
        return \
            {ScheduleInstance(program=row.Program, date=row.SchemaRecord.date)
                for row in self.session.execute(stmt).all()}

    @staticmethod
    def _prolonged_grid(grid: ScheduleSet) -> ScheduleSet:
        week = rd.relativedelta(days=7)
        return \
            {ScheduleInstance(program=obj.program, date=obj.date + week)
                for obj in grid}

    @staticmethod
    def _apply_filters(stmt: Select, filters: dict):
        for filter_pointer, filter_val in filters.items():
            if filter_val:
                cond = object.__getattribute__(tables.Program, filter_pointer) == filter_val
                stmt = stmt.where(cond)
        return stmt

    def _count_booked_classes(
        self,
        schema: tables.ScheduleSchema,
        filters,
    ) -> ScheduleSet:
        BC, SSR = tables.BookedClasses, tables.schedule_schema_record
        class_date = utils.calc_date_sql(tables.SchemaRecord.week_day, tables.SchemaRecord.day_time)
        stmt = self._apply_filters((
            select(tables.Program, tables.SchemaRecord, BC.date, func.count(BC.id))
            .join(tables.SchemaRecord)
            .join(BC)
            .join(SSR)
            .where(SSR.c.schedule_schema == schema.id)
            .where(tables.Program.available_registration.is_(True))
            .where(
                    or_(
                        BC.date == utils.tz_date_sql(class_date),
                        BC.date == utils.tz_date_sql(class_date + utils.make_interval(days=7))
                    ) & (BC.date > func.now())
            )
            .group_by(tables.Program, tables.SchemaRecord, BC.date)
        ), filters)
        return \
            {ScheduleInstance(program=row.Program, date=row.date, booked_places=row.count)
                for row in self.session.execute(stmt).all()}

    def construct_schedule(self, filters) -> list[models.ScheduleRecord]:
        self._validate_active_schema()
        active_schema = self.schema_service.active_schema
        next_week_schema = self.schema_service.next_week_schema

        response = self._count_booked_classes(active_schema, filters)  # получаем занятия, на которые регистрировались
        grid = self._get_grid(active_schema, filters)
        response.update(grid)  # добавляем к ним невключенные занятия с этой недели (без зарегистрировавшихся)

        if not next_week_schema:
            response |= self._prolonged_grid(grid)  # добавить к ним невключенные занятия со след. неделе
        else:
            counted_grid = self._count_booked_classes(next_week_schema, filters)  # пересчитываем записавшихся по след. неделе
            grid = self._get_grid(next_week_schema, filters)
            counted_grid |= self._prolonged_grid(grid)
            response.update(counted_grid)

        return [obj.to_schema() for obj in response]
