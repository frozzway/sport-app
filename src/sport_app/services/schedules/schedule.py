import datetime
from typing import (
    Optional,
    NamedTuple,
    Any
)
from collections.abc import Iterable

from dateutil import relativedelta as rd
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.sql.expression import Select

from .schema import SchemaService
from ...database import get_session
from ... import (
    tables,
    models,
    utils
)


class ScheduleInstance(NamedTuple):
    """
    Определяет занятие в сформированном расписании. Используется как элемент множеств, возвращаемых _get_grid() и
    _count_booked_classes(). Множества, set[ScheduleInstance], применяются в construct_schedule() для уменьшения
    сложности алгоритма construct_schedule()
    """
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

    def to_model(self) -> models.ScheduleRecord:
        place_limit = self.program.place_limit
        places_available = None
        registration_opens_at = None

        if self.program.available_registration and self.date >= utils.today():
            if place_limit:
                places_available = place_limit - self.booked_places
            if self.program.registration_opens:
                registration_period = rd.relativedelta(days=self.program.registration_opens, hour=16)
                registration_opens_at = self.date - registration_period

        return models.ScheduleRecord(
                program=self.program.to_model(),
                places_available=places_available,
                registration_opens_at=registration_opens_at,
                date=self.date,
            )


class ScheduleService:
    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        self.session = session
        self.schema_service = SchemaService(session)

    def _validate_active_schema(self):
        next_week_schema = self.schema_service.next_week_schema
        active_schema = self.schema_service.active_schema
        if next_week_schema:
            start_date = next_week_schema.to_be_active_from
            if utils.now() > start_date:
                next_week_schema.to_be_active_from = None
                next_week_schema.active = True
                active_schema.active = False
                self.session.commit()
        return active_schema, next_week_schema

    def _get_grid(
        self,
        schema: tables.ScheduleSchema,
        filters: dict[str, Any]
    ) -> set[ScheduleInstance]:
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
    def _prolong_grid(grid: Iterable[ScheduleInstance]) -> set[ScheduleInstance]:
        week = rd.relativedelta(days=7)
        return \
            {ScheduleInstance(program=obj.program, date=obj.date + week)
                for obj in grid}

    @staticmethod
    def _apply_filters(stmt: Select, filters: dict[str, Any]):
        for filter_pointer, filter_val in filters.items():
            if filter_val:
                cond = object.__getattribute__(tables.Program, filter_pointer) == filter_val
                stmt = stmt.where(cond)
        return stmt

    def _count_booked_classes(self, filters: dict[str, Any]) -> set[ScheduleInstance]:
        """
        Обращается к базе данных с целью подсчитать количество забронированных мест на занятия. Выполняет
        запрос, в котором есть join с таблицей BookedClasses. В связи с чем возвращает только те занятия
        (ScheduleInstance), на которые кто-то записался.
        """
        BC = tables.BookedClasses
        stmt = self._apply_filters((
            select(tables.Program, BC.date, func.count(BC.id))
            .join(BC)
            .where(BC.date > func.now())
            .group_by(tables.Program, BC.date)
        ), filters)
        return \
            {ScheduleInstance(program=row.Program, date=row.date, booked_places=row.count)
                for row in self.session.execute(stmt).all()}

    def construct_schedule(self, filters: dict[str, Any]) -> list[models.ScheduleRecord]:
        active_schema, next_week_schema = self._validate_active_schema()
        booked_classes = self._count_booked_classes(filters)
        current_week_classes = self._get_grid(active_schema, filters)
        if next_week_schema:
            grid = self._get_grid(next_week_schema, filters)
            next_week_classes = self._prolong_grid(grid)
        else:
            next_week_classes = self._prolong_grid(current_week_classes)
        response = booked_classes | current_week_classes | next_week_classes
        return [obj.to_model() for obj in response]
