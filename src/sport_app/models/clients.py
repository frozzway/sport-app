from typing import Any
from pydantic import BaseModel, Field, Json


class BaseClient(BaseModel):
    credentials: str = Field(max_length=100)
    phone: str
    additional_data: Json


class Client(BaseClient):
    id: int
    additional_data: Any

    class Config:
        orm_mode = True


class ClientMinimum(BaseModel):
    id: int
    credentials: str = Field(max_length=100)

    class Config:
        orm_mode = True


class CreateClient(BaseClient):
    pass


class ClientUpdate(BaseClient):
    pass
