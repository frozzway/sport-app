from typing import Optional
from typing import Union

from pydantic import (
    BaseModel,
    Field
)


class Category(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    color: Optional[str] = Field(max_length=20)

    class Config:
        orm_mode = True


class Placement(BaseModel):
    name: str = Field(min_length=3, max_length=100)

    class Config:
        orm_mode = True


class BaseInstructor(BaseModel):
    credentials: str = Field(min_length=3, max_length=100)
    phone: str


class InstructorCreate(BaseInstructor):
    pass


class InstructorUpdate(BaseInstructor):
    pass


class Instructor(BaseInstructor):
    id: int
    photo_src: Optional[str]

    class Config:
        orm_mode = True


class InstructorPublic(BaseModel):
    id: int
    credentials: str
    photo_src: Optional[str]

    class Config:
        orm_mode = True


class BaseProgram(BaseModel):
    name: str = Field(max_length=100)
    category: Category
    placement: Placement
    instructor: InstructorPublic
    paid: bool
    place_limit: int = None
    registration_opens: int = None
    available_registration: Optional[bool]


class CreateProgram(BaseProgram):
    category: Union[Category, str]
    placement: Union[Placement, str]
    instructor: Union[Instructor, int]


class Program(BaseProgram):
    id: int

    class Config:
        orm_mode = True
