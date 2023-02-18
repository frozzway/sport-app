import datetime

from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ..models import Client, CreateClient, ClientUpdate
from ..services import ClientService

router = APIRouter(
    prefix='/client',
    tags=['clients']
)


@router.get(
    '/{client_id}',
    response_model=Client
)
def get_client(
    client_id: int,
    client_service: ClientService = Depends(),
):
    return client_service.get_client(client_id)


@router.post(
    '/',
    response_model=Client,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    client_data: CreateClient,
    client_service: ClientService = Depends(),
):
    return client_service.create_client(client_data)


@router.put(
    '/{client_id}',
    response_model=Client
)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    client_service: ClientService = Depends(),
):
    return client_service.update_client(client_id, client_data)


@router.post(
    '/{client_id}/book',
    status_code=status.HTTP_204_NO_CONTENT
)
def book_client(
    client_id: int,
    program: int,
    date: datetime.datetime,
    client_service: ClientService = Depends(),
):
    return client_service.book_client(client_id, program, date)

