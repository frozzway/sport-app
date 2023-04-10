from sqlalchemy import (
    Column, String, Integer,
    ForeignKey, DateTime, Time, Boolean, JSON,
    Table, UniqueConstraint, Enum
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .constructor import constructor
from .models import (
    program_to_model,
    record_to_model,
    Roles
)
from .utils import *


Base = declarative_base(constructor=constructor)


class Category(Base):
    __tablename__ = "category"

    name = Column(String, primary_key=True)
    color = Column(String)

    programs = relationship("Program", back_populates="category_obj")


class Placement(Base):
    __tablename__ = "placement"

    name = Column(String, primary_key=True)


class Instructor(Base):
    __tablename__ = "instructor"

    id = Column(Integer, primary_key=True)
    credentials = Column(String)
    phone = Column(String, unique=True)
    photo_token = Column(String, nullable=True)

    programs = relationship("Program", back_populates="instructor_obj")


class Program(Base):
    __tablename__ = "program"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String, ForeignKey("category.name", onupdate="CASCADE"))
    placement = Column(String, ForeignKey("placement.name", onupdate="CASCADE"))
    instructor = Column(Integer, ForeignKey("instructor.id"))
    paid = Column(Boolean)
    place_limit = Column(Integer, nullable=True)
    registration_opens = Column(Integer, nullable=True)
    available_registration = Column(Boolean, default=False)

    category_obj = relationship("Category", back_populates="programs")
    instructor_obj = relationship("Instructor", back_populates="programs")

    to_model = program_to_model

    def registration_opens_at(self, class_date: datetime.datetime) -> datetime.datetime:
        if not self.registration_opens:
            return day_stub()
        pre_days = rd.relativedelta(days=self.registration_opens, hour=16)
        return class_date - pre_days


schedule_schema_record = Table(
    "schedule_schema_record",
    Base.metadata,
    Column("schedule_schema", ForeignKey("schedule_schema.id", ondelete="CASCADE"), primary_key=True),
    Column("schema_record", ForeignKey("schema_record.id", ondelete="CASCADE"), primary_key=True),
)


class SchemaRecord(Base):
    __tablename__ = "schema_record"

    id = Column(Integer, primary_key=True)
    week_day = Column(Integer)
    day_time = Column(Time)
    duration = Column(Integer)
    program = Column(Integer, ForeignKey("program.id", ondelete="CASCADE"))

    to_model = record_to_model

    @property
    def date(self):
        return calculate_date(self.week_day, self.day_time)


class ScheduleSchema(Base):
    __tablename__ = "schedule_schema"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean, default=False)
    to_be_active_from = Column(DateTime(timezone=True), nullable=True)

    records = relationship("SchemaRecord", secondary=schedule_schema_record)


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    credentials = Column(String)
    phone = Column(String, unique=True)
    additional_data = Column(JSON)


class BookedClasses(Base):
    __tablename__ = "booked_classes"

    id = Column(Integer, primary_key=True)
    client = Column(Integer, ForeignKey("client.id", ondelete="CASCADE"))
    program = Column(Integer, ForeignKey("program.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            'client',
            'program',
            'date',
            name='one_booking_per_client_uc'
        ),
    )


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(Enum(Roles))
