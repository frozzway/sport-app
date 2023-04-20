import datetime
from typing import Optional

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.sql import and_

from . import (
    SchemaService,
    ProgramService
)
from ..database import get_session
from .. import (
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

    def get_many(
        self,
        staff_member: models.Staff
    ) -> list[tables.Client]:
        clients = (
            self.session
            .query(tables.Client)
            .all()
        )
        if staff_member.role == 'staff_role.admin':
            clients = [models.Client.from_orm(c) for c in clients]
        else:
            clients = [models.ClientMinimum.from_orm(c) for c in clients]
        return clients

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

    def delete_client(
        self,
        client_id: int
    ):
        client = self.get_client(client_id)
        try:
            self.session.delete(client)
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT)

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
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Регистрация закрыта")

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
            ).scalar()
        )
        if schema_record not in schema.records:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if program.place_limit:
            BC = tables.BookedClasses
            booked_places = self.session.execute(
                select(func.count(BC.id))
                .where(BC.date == date)
                .where(BC.program == program.id)
            ).scalar_one()
            available_places = program.place_limit - booked_places
            if not available_places:
                raise HTTPException(status.HTTP_409_CONFLICT, detail="Отсутствуют свободные места")
        try:
            place = tables.BookedClasses(client=client_id, program=program.id, date=date)
            self.session.add(place)
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Клиент уже записан или не найден")

    def remove_client_booking(
        self,
        client_id: int,
        program: int,
        date: datetime.datetime
    ):
        if date < utils.now():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)
        record = self.session.execute(
            select(tables.BookedClasses)
            .where(and_(
                tables.BookedClasses.program == program,
                tables.BookedClasses.client == client_id,
                tables.BookedClasses.date == date)
            )).scalar()
        if not record:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        self.session.delete(record)
        self.session.commit()




