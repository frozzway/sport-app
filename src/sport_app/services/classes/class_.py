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
    schemas
)


class ClassService:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def _get(
        self,
        class_id: int
    ) -> Optional[tables.Class]:
        class_ = (
            self.session
            .query(tables.Class)
            .filter(tables.Class.id == class_id)
            .first()
        )
        if not class_:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return class_

    def get(
        self,
        class_id: int
    ) -> schemas.Class:
        class_ = self._get(class_id)
        return class_.to_schema()

    def get_many(self) -> list[schemas.Class]:
        classes = (
            self.session
            .query(tables.Class)
            .all()
        )
        return [c.to_schema()
                for c in classes]

    def create_class(
        self,
        data: schemas.CreateClass
    ) -> schemas.Class:
        class_ = tables.Class(
            **data.dict()
        )
        try:
            self.session.add(class_)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT)
        return class_.to_schema()