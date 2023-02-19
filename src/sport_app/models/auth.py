import enum
from typing import Union

from pydantic import BaseModel


Roles = enum.Enum('staff_role', ['admin', 'operator'])


class BaseStaff(BaseModel):
    email: str
    username: str


class StaffCreate(BaseStaff):
    password: str


class Staff(BaseStaff):
    id: int
    role: Union[str, Roles]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'