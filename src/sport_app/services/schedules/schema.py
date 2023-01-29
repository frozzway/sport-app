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
from sqlalchemy.orm import Session, aliased
from sqlalchemy import delete, select, func, tuple_
from sqlalchemy.sql import alias, or_, and_

from sport_app.database import get_session

from sport_app import (
    tables,
    models,
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
        schema_data: models.SchemaCreate,
    ) -> tables.ScheduleSchema:
        base_schema = self._get_schema(schema_data.base_schema) if schema_data.base_schema else None
        schema = tables.ScheduleSchema(
            name=schema_data.name
        )
        active_schema = self.active_schema
        if not active_schema:
            schema.active = True
        self.session.add(schema)
        if base_schema:
            schema.records = base_schema.records
        self.session.commit()
        return schema

    def delete_schema(
        self,
        schema_id: int
    ):
        schema = self._get_schema(schema_id)
        if schema.active:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.session.delete(schema)
        self.session.commit()

    def _compare_schemas(
        self,
        schema: tables.ScheduleSchema,
        target_schema: tables.ScheduleSchema,
        next_week=False,
    ):
        """
        Снимает бронирования клиентов на занятия, которые отсутствуют в новой схеме, но присутствуют в старой
        :param schema: новая схема
        :param target_schema: старая схема
        :param next_week: удаляет записи со следующей недели
        :return:
        """
        interval = rd.relativedelta(days=7) if next_week else rd.relativedelta()
        target = set(target_schema.records) - set(schema.records)
        obj_to_remove = []
        for r in target:
            date = r.date + interval
            if date > utils.now():
                obj_to_remove.append((r.Class, date))
        B = aliased(tables.BookedClasses)
        rows = (
            self.session.query(B)
            .where(tuple_(B.class_id, B.date).in_(obj_to_remove))
            .all()
        )
        for row in rows:
            self.session.delete(row)
        self.session.commit()

    # Нуждается в тестировании
    def update_schema(
        self,
        schema_id: int,
        schema_data: models.SchemaUpdate,
    ) -> tables.ScheduleSchema:
        schema = self._get_schema(schema_id)
        active_schema = self.active_schema
        next_week_schema = self.next_week_schema

        # активация схемы
        if schema_data.active:
            self._compare_schemas(schema, active_schema)
            active_schema.active = False
            schema.active = True
            # если активируется схема, которая запланирована на следующую неделю
            if next_week_schema and next_week_schema.id == schema_id:
                schema.to_be_active_from = None

        # деактивация схемы
        if schema_data.active is False:
            if schema.id == active_schema.id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="Не допускается деактивация схемы")

        # активация схемы на следующую неделю
        if schema_data.activate_next_week:
            if next_week_schema:
                self._compare_schemas(schema, next_week_schema, next_week=True)
                next_week_schema.to_be_active_from = None
            schema.to_be_active_from = utils.next_mo()
            if schema.active:
                schema.to_be_active_from = None

        for field, value in schema_data:
            if value:
                setattr(schema, field, value)
        self.session.commit()
        return schema

    def get_schema_records(
        self,
        schema_id: int
    ) -> list[models.SchemaRecord]:
        schedule_schema = self._get_schema(schema_id)
        return [record.to_schema() for record in schedule_schema.records]

    def include_records_in_schema(
        self,
        schema_id: int,
        records_to_include: list[int],
    ) -> list[int]:
        schema = self._get_schema(schema_id)
        records = set((r.id for r in schema.records))
        existing_records = (
            self.session
            .query(tables.SchemaRecord)
            .all()
        )
        records.update((r for r in records_to_include if r in existing_records))
        schema.records = records
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