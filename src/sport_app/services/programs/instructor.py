from typing import (
    Optional
)

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_session

from ... import (
    tables,
    models
)


class InstructorService:
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Номер телефона уже имеется в базе'
    )

    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def _get(
        self,
        instructor_id: int
    ) -> Optional[tables.Instructor]:
        instructor = (
            self.session
            .query(tables.Instructor)
            .filter(tables.Instructor.id == instructor_id)
            .first()
        )
        if not instructor:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return instructor

    def get_instructor(
        self,
        instructor_id: int
    ) -> tables.Instructor:
        instructor = self._get(instructor_id)
        return instructor

    def get_many(
        self
    ) -> list[tables.Instructor]:
        instructors = (
            self.session
            .query(tables.Instructor)
            .all()
        )
        return instructors

    def create_instructor(
        self,
        instructor_data: models.InstructorCreate
    ) -> tables.Instructor:
        instructor = tables.Instructor(
            **instructor_data.dict()
        )
        try:
            self.session.add(instructor)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise InstructorService.exception from None
        return instructor

    def delete_instructor(
        self,
        instructor_id: int
    ):
        instructor = self._get(instructor_id)
        try:
            self.session.delete(instructor)
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Инструктор задействован в расписании.")
        return

    def update_instructor(
        self,
        instructor_id: int,
        instructor_data: models.InstructorUpdate
    ) -> tables.Instructor:
        instructor = self._get(instructor_id)
        for field, value in instructor_data:
            setattr(instructor, field, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise InstructorService.exception from None
        return instructor