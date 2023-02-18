from typing import Optional, Union
from collections.abc import Iterable

from dateutil import relativedelta as rd

from fastapi import (
    Depends,
    HTTPException,
    status
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, func, tuple_
from sqlalchemy.sql import or_, and_

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
        if schema.active or schema.to_be_active_from:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail="Запрещается удаление активной схемы")
        self.session.delete(schema)
        self.session.commit()

    def _compare_schemas(
        self,
        schema: tables.ScheduleSchema,
        target_schema: tables.ScheduleSchema,
        next_week=False,
    ):
        """
        Генерирует список занятий, которые отсутствуют в schema, но присутствуют в target_schema,
        передает список на снятие бронирования
        """
        records = set(target_schema.records) - set(schema.records)
        self._remove_booking(records, next_week=next_week)

    def _remove_booking(
        self,
        records: Union[Iterable[tables.SchemaRecord], Iterable[int]],
        next_week=False
    ):
        """
        Снимает бронирование клиентов с занятий начиная с now()
        :param next_week: снимет на следующей неделе
        """
        if isinstance(next(iter(records), None), int):
            records = (
                self.session
                .query(tables.SchemaRecord)
                .where(tables.SchemaRecord.id.in_(records))
                .all()
            )
        interval = rd.relativedelta(days=7) if next_week else rd.relativedelta()
        obj_to_remove = [(r.program, r.date + interval)
                         for r in records
                         if r.date+interval > utils.now()]
        B = tables.BookedClasses
        self.session.execute(
            delete(B)
            .where(tuple_(B.program, B.date).in_(obj_to_remove))
            .all()
        )
        self.session.flush()

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
            if not next_week_schema:
                self._compare_schemas(schema, active_schema, next_week=True)
            active_schema.active = False
            schema.active = True
            # если активируется схема, которая запланирована на следующую неделю
            if next_week_schema and schema.id == next_week_schema.id:
                schema.to_be_active_from = None

        # деактивация схемы
        if schema_data.active is False:
            if schema.id == active_schema.id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="Не допускается деактивация схемы")

        # активация схемы на следующую неделю
        if schema_data.activate_next_week:
            if schema.active:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="Схема уже активна")
            if next_week_schema:
                self._compare_schemas(schema, next_week_schema, next_week=True)
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
    ) -> list[models.SchemaRecord]:
        schedule_schema = self._get_schema(schema_id)
        return [record.to_model() for record in schedule_schema.records]

    def include_records_in_schema(
        self,
        schema_id: int,
        records_to_include: Iterable[int],
    ) -> list[int]:
        schema = self._get_schema(schema_id)
        records = set((r.id for r in schema.records))
        records.update(records_to_include)
        new_records = (
            self.session
            .query(tables.SchemaRecord)
            .filter(tables.SchemaRecord.id.in_(records))
            .all()
        )
        schema.records = new_records
        self.session.commit()
        return [r.id for r in new_records]

    def exclude_records_from_schema_(
        self,
        schema_id: int,
        records_to_exclude: list[int]
    ):
        schema = self._get_schema(schema_id)

        if schema.active:
            self._remove_booking(records_to_exclude)
            if not self.next_week_schema:
                self._remove_booking(records_to_exclude, next_week=True)
        elif schema.to_be_active_from:
            self._remove_booking(records_to_exclude, next_week=True)

        table = tables.schedule_schema_record
        self.session.execute(
            delete(table)
            .where(table.schema_record.in_(records_to_exclude))
            .where(table.schedule_schema == schema_id)
        )
        self.session.flush()

    def exclude_records_from_schema(
        self,
        schema_id: int,
        records_to_exclude: list[int]
    ):
        self.exclude_records_from_schema_(schema_id, records_to_exclude)
        self.session.commit()
