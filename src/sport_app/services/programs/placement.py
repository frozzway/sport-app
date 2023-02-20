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

    def get_placement(
        self,
        name: str
    ) -> tables.Placement:
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

    def create_placement(
        self,
        data: models.Placement
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

    def update_placement(
        self,
        name: str,
        data: models.Placement
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

    def delete_placement(
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