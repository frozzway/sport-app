import datetime
from typing import (
    Optional,
    NamedTuple
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
from sqlalchemy.sql.expression import Select

from . import (
    SchemaService,
    ProgramService
)
from sport_app.database import get_session
from sport_app import (
    tables,
    models,
    utils
)


class ClientService:
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Номер телефона уже имеется в базе'
    )

    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        self.session = session
        self.schema_service = SchemaService(session)
        self.program_service = ProgramService(session)

    def _get_client(
        self,
        client_id: int
    ) -> Optional[tables.Client]:
        client = (
            self.session
            .query(tables.Client)
            .where(tables.Client.id == client_id)
            .scalar()
        )
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return client

    def get_client(
        self,
        client_id: int
    ) -> tables.Client:
        return self._get_client(client_id)

    def create_client(
        self,
        client_data: models.CreateClient
    ) -> tables.Client:
        client = tables.Client(
            **client_data.dict()
        )
        try:
            self.session.add(client)
            self.session.commit()
        except IntegrityError:
            raise ClientService.exception from None
        return client

    def update_client(
        self,
        client_id: int,
        client_data: models.ClientUpdate
    ) -> tables.Instructor:
        client = self._get_client(client_id)
        for field, value in client_data:
            setattr(client, field, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ClientService.exception from None
        return client

    def book_client(
        self,
        client_id: int,
        program: int,
        date: datetime.datetime,
    ):
        """
        Бронирование клиента на занятие.
        :param client_id: id клиента
        :param program: id программы
        :param date: дата занятия
        """
        program = self.program_service.get(program)
        if any([
            not program.available_registration,
            date < utils.now(),
            utils.now() < program.registration_opens_at(date),
        ]):
            raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)

        if all([
            date >= utils.next_mo(),
            nw_schema := self.schema_service.next_week_schema
        ]):
            schema = nw_schema
        else:
            schema = self.schema_service.active_schema

        schema_record = (
            self.session
            .query(tables.SchemaRecord)
            .where(and_(
                tables.SchemaRecord.week_day == date.weekday(),
                tables.SchemaRecord.day_time == date.time(),
                tables.SchemaRecord.program == program.id)
            )
            .scalar()
        )
        if schema_record not in schema.records:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        BC = tables.BookedClasses
        stmt = (
            select(func.count(BC.id))
            .where(BC.date == date)
            .where(BC.program == program.id)
        )
        booked_places = self.session.execute(stmt).scalar_one()
        available_places = program.place_limit - booked_places
        if not available_places:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Отсутствуют свободные места")
        try:
            place = tables.BookedClasses(client=client_id, program=program.id, date=date)
            self.session.add(place)
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Клиент уже забронирован или не найден")