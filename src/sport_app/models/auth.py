from pydantic import BaseModel


class BaseStaff(BaseModel):
    email: str
    username: str


class StaffCreate(BaseStaff):
    password: str


class Staff(BaseStaff):
    id: int
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'