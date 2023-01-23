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


class RecordService:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def create_record(
        self,
        record_data: schemas.SchemaRecordCreate,
    ) -> schemas.SchemaRecord:
        schedule_record = tables.SchemaRecord(
            **record_data.dict()
        )
        try:
            self.session.add(schedule_record)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Занятие отсутствует")
        return schedule_record.to_schema()

