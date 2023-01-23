from typing import (
    Optional
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

from ..database import get_session

from .. import (
    tables,
    schemas,
    utils
)


class SchemaService:
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

    @property
    def active_schema(self) -> Optional[tables.ScheduleSchema]:
        schema = (
            self.session
            .query(tables.ScheduleSchema)
            .filter(tables.ScheduleSchema.active)
            .scalar()
        )
        return schema

    @property
    def next_week_schema(self) -> Optional[tables.ScheduleSchema]:
        schema = (
            self.session
            .query(tables.ScheduleSchema)
            .filter(tables.ScheduleSchema.to_be_active_from == utils.next_mo())
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
        schema_data: schemas.SchemaCreate,
    ) -> tables.ScheduleSchema:
        schema = tables.ScheduleSchema(
            **schema_data.dict()
        )
        active_schema = self.active_schema()
        if not active_schema:
            schema.active = True
        elif schema_data.active:
            active_schema.active = False
        self.session.add(schema)
        self.session.commit()
        return schema

    # Нуждается в доработке
    def update_schema(
        self,
        schema_id: int,
        schema_data: schemas.SchemaUpdate,
    ) -> tables.ScheduleSchema:
        schema = self._get_schema(schema_id)
        if schema_data.active:
            active_schema = self.active_schema()
            active_schema.active = False
        if schema_data.activate_next_week:
            next_week_schema = self.next_week_schema()
            next_week_schema.to_be_active_from = None
            schema.to_be_active_from = utils.next_mo()
        for field, value in schema_data:
            if value:
                setattr(schema, field, value)
        self.session.commit()
        return schema

    def get_schema_records(
        self,
        schema_id: int
    ) -> list[schemas.SchemaRecord]:
        schedule_schema = self._get_schema(schema_id)
        return [record.to_schema() for record in schedule_schema.records]

    def include_records_in_schema(
        self,
        schema_id: int,
        records_to_include: list[int],
    ) -> list[int]:
        schema = self._get_schema(schema_id)
        records = set((r.id for r in schema.records))
        records.update(records_to_include)
        existing_records_to_include = (
            self.session
            .query(tables.SchemaRecord)
            .filter(tables.SchemaRecord.id.in_(records))
            .all()
        )
        schema.records = existing_records_to_include
        self.session.commit()
        return [r.id for r in schema.records]

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