from typing import (
    Optional
)

from dateutil.utils import today
from dateutil.tz import gettz
from dateutil import relativedelta as rd

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy.sql import alias

from ..settings import settings

from ..database import (
    get_session,
)

from .. import (
    tables,
    schemas
)


def next_mo():
    TODAY = today(gettz(settings.timezone))
    return TODAY + rd.relativedelta(days=+1, weekday=rd.MO)


class ScheduleService:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def _get_schema(
        self,
        schema_id: int,
    ) -> tables.ScheduleSchema:
        schema = (
            self.session
            .query(tables.ScheduleSchema)
            .filter(tables.ScheduleSchema.id == schema_id)
            .scalar()
        )
        if not schema:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return schema

    def _get_active_schema(self) -> Optional[tables.ScheduleSchema]:
        schema = (
            self.session
            .query(tables.ScheduleSchema)
            .filter(tables.ScheduleSchema.active)
            .scalar()
        )
        return schema

    def _get_next_week_schema(self) -> Optional[tables.ScheduleSchema]:
        schema = (
            self.session
            .query(tables.ScheduleSchema)
            .filter(tables.ScheduleSchema.to_be_active_from == next_mo())
            .scalar()
        )
        return schema

    def get_many_schemas(self) -> list[tables.ScheduleSchema]:
        schemas = (
            self.session
            .query(tables.ScheduleSchema)
            .all()
        )
        return schemas

    def create_schema(
        self,
        schema_data: schemas.ScheduleSchemaCreate,
    ) -> tables.ScheduleSchema:
        schema = tables.ScheduleSchema(
            **schema_data.dict()
        )
        active_schema = self._get_active_schema()
        if not active_schema:
            schema.active = True
        elif schema_data.active:
            active_schema.active = False
        self.session.add(schema)
        self.session.commit()
        return schema

    def update_schema(
        self,
        schema_id: int,
        schema_data: schemas.ScheduleSchemaUpdate,
    ) -> tables.ScheduleSchema:
        schema = self._get_schema(schema_id)
        if schema_data.active:
            active_schema = self._get_active_schema()
            active_schema.active = False
        if schema_data.activate_next_week:
            next_week_schema = self._get_next_week_schema()
            next_week_schema.to_be_active_from = None
            schema.to_be_active_from = next_mo()
        for field, value in schema_data:
            if value:
                setattr(schema, field, value)
        self.session.commit()
        return schema

    def create_record(
        self,
        record_data: schemas.ScheduleRecordCreate,
    ) -> schemas.ScheduleRecord:
        schedule_record = tables.ScheduleRecord(
            **record_data.dict()
        )
        try:
            self.session.add(schedule_record)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Занятие отсутствует")
        return schedule_record.to_schema()

    def get_records_in_schema(self, schema_id: int) -> list[schemas.ScheduleRecord]:
        schedule_schema = self._get_schema(schema_id)
        return [record.to_schema() for record in schedule_schema.schedule_records]

    def include_records_in_schema(
        self,
        schema_id: int,
        records_to_include: list[int],
    ) -> list[int]:
        schema = self._get_schema(schema_id)
        records = set((r.id for r in schema.schedule_records))
        records.update(records_to_include)
        existing_records_to_include = (
            self.session
            .query(tables.ScheduleRecord)
            .filter(tables.ScheduleRecord.id.in_(records))
            .all()
        )
        schema.schedule_records = existing_records_to_include
        self.session.commit()
        return [r.id for r in schema.schedule_records]

    # Нуждается в доработке
    def exclude_records_from_schema(
        self,
        schema_id: int,
        records_to_exclude: list[int]
    ):
        schema = self._get_schema(schema_id)
        table = alias(tables.schedule_schema_record)
        self.session.execute(
            delete(table)
            .where(table.c.schedule_record.in_(records_to_exclude))
            .where(table.c.schedule_schema == schema_id)
        )
        self.session.commit()
