from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


class Category(BaseModel):
    name: str = Field(max_length=100)

    class Config:
        orm_mode = True


class Placement(BaseModel):
    name: str = Field(max_length=100)

    class Config:
        orm_mode = True


class BaseInstructor(BaseModel):
    credentials: str = Field(max_length=100)
    phone: str


class InstructorCreate(BaseInstructor):
    pass


class InstructorUpdate(BaseInstructor):
    pass


class Instructor(BaseInstructor):
    id: int

    class Config:
        orm_mode = True


class InstructorPublic(BaseModel):
    id: int
    credentials: str

    class Config:
        orm_mode = True


class BaseClass(BaseModel):
    program: str = Field(max_length=100)
    category: Category
    placement: Placement
    instructor: InstructorPublic
    paid: bool
    place_limit: int = None
    registration_opens: int = None
    available_registration: Optional[bool]


class CreateClass(BaseClass):
    pass


class Class(BaseClass):
    id: int

    class Config:
        orm_mode = True
