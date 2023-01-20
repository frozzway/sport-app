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

from ..database import get_session

from .. import (
    tables,
    schemas
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
        data: schemas.Category
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
        data: schemas.Category
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


class PlacementService:
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Помещение с таким наименованием уже существует'
    )

    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def get(
        self,
        name: str
    ) -> Optional[tables.Placement]:
        placement = self._get(name)
        return placement

    def get_many(
        self
    ) -> list[tables.Placement]:
        placements = (
            self.session
            .query(tables.Placement)
            .all()
        )
        return placements

    def create(
        self,
        data: schemas.Placement
    ) -> tables.Placement:
        placement = tables.Placement(
            **data.dict()
        )
        try:
            self.session.add(placement)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise PlacementService.exception from None
        return placement

    def update(
        self,
        name: str,
        data: schemas.Placement
    ) -> tables.Placement:
        placement = self._get(name)
        for field, value in data:
            setattr(placement, field, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise PlacementService.exception from None
        return placement

    def delete(
        self,
        name: str,
    ):
        placement = self._get(name)
        self.session.delete(placement)
        self.session.commit()

    def _get(
        self,
        name: str
    ) -> Optional[tables.Placement]:
        placement = (
            self.session
            .query(tables.Placement)
            .filter(tables.Placement.name == name)
            .first()
        )
        if not placement:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return placement


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

    def get(
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

    def create(
        self,
        instructor_data: schemas.InstructorCreate
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

    def delete(
        self,
        instructor_id: int
    ):
        instructor = self._get(instructor_id)
        self.session.delete(instructor)
        self.session.commit()
        return

    def update(
        self,
        instructor_id: int,
        instructor_data: schemas.InstructorUpdate
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
