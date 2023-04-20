from typing import (
    Optional
)

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_session

from ... import (
    tables,
    models
)


class ProgramService:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def _get(
        self,
        program_id: int
    ) -> Optional[tables.Program]:
        program = (
            self.session
            .query(tables.Program)
            .filter(tables.Program.id == program_id)
            .first()
        )
        if not program:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return program

    def get(
        self,
        program_id: int
    ) -> tables.Program:
        program = self._get(program_id)
        return program

    def get_many(self) -> list[models.Program]:
        programs = (
            self.session
            .query(tables.Program)
            .all()
        )
        return [c.to_model()
                for c in programs]

    def create_program(
        self,
        data: models.CreateProgram
    ) -> models.Program:
        program = tables.Program(
            **data.dict()
        )
        try:
            self.session.add(program)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT)
        return program.to_model()

    def delete_program(self, program_id: int):
        program = self._get(program_id)
        try:
            self.session.execute(delete(tables.Program).where(tables.Program.id == program_id))
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT)