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


class CategoryService:
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Категория с таким наименованием уже существует'
    )

    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def get(
        self,
        name: str
    ) -> Optional[tables.Category]:
        category = self._get(name)
        return category

    def get_many(
        self
    ) -> list[tables.Category]:
        categories = (
            self.session
            .query(tables.Category)
            .all()
        )
        return categories

    def create(
        self,
        data: models.Category
    ) -> tables.Category:
        category = tables.Category(
            **data.dict()
        )
        try:
            self.session.add(category)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise CategoryService.exception from None
        return category

    def update(
        self,
        name: str,
        data: models.Category
    ) -> tables.Category:

        category = self._get(name)
        for field, value in data:
            setattr(category, field, value)
        self.session.commit()
        return category

    def delete(
        self,
        name: str,
    ):
        category = self._get(name)
        self.session.delete(category)
        self.session.commit()

    def _get(
        self,
        name: str
    ) -> Optional[tables.Category]:
        category = (
            self.session
            .query(tables.Category)
            .filter(tables.Category.name == name)
            .first()
        )
        if not category:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return category