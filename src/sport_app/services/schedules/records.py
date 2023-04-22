from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import delete

from .schema import SchemaService
from ...database import get_session
from ... import (
    tables,
    models
)


class RecordService:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session
        self.schema_service = SchemaService(session)

    def get_or_create_record(
        self,
        record_data: models.SchemaRecordCreate,
    ) -> models.SchemaRecord:
        schedule_record = self.session.query(tables.SchemaRecord).filter_by(**record_data.dict()).first()
        if not schedule_record:
            schedule_record = self.create_record(record_data)
        return schedule_record.to_model()

    def create_record(
        self,
        record_data: models.SchemaRecordCreate,
    ) -> tables.SchemaRecord:
        schedule_record = tables.SchemaRecord(
            **record_data.dict()
        )
        try:
            self.session.add(schedule_record)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Тренировочная программа не существует")
        return schedule_record

    def get_many(self) -> list[models.SchemaRecord]:
        records = self.session.query(tables.SchemaRecord).all()
        return [record.to_model() for record in records]

    def delete_record(
        self,
        record_id: int
    ):
        record = self._get_record(record_id)
        active_schema = self.schema_service.active_schema
        next_week_schema = self.schema_service.next_week_schema

        if record in active_schema.records:
            self.schema_service.exclude_records_from_schema_(active_schema.id, [record.id])
        if next_week_schema and record in next_week_schema.records:
            self.schema_service.exclude_records_from_schema_(next_week_schema.id, [record.id])

        self.session.execute(
            delete(tables.SchemaRecord)
            .where(tables.SchemaRecord.id == record_id)
        )
        self.session.commit()

    def _get_record(
        self,
        record_id: int
    ) -> tables.SchemaRecord:
        record = (
            self.session
            .query(tables.SchemaRecord)
            .where(tables.SchemaRecord.id == record_id)
            .first()
        )
        if not record:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return record

