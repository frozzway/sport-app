from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    ForeignKey,
    DateTime, Time,
    Boolean,
    JSON,
    Table,
)

from .constructor import constructor

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .schemas import (
    class_to_schema,
    record_to_schema
)


Base = declarative_base(constructor=constructor)


class Category(Base):
    __tablename__ = "category"

    name = Column(String, primary_key=True)


class Placement(Base):
    __tablename__ = "placement"

    name = Column(String, primary_key=True)


class Instructor(Base):
    __tablename__ = "instructor"

    id = Column(Integer, primary_key=True)
    credentials = Column(String)
    phone = Column(String, unique=True)

    classes = relationship("Class", back_populates="instructor_")


class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True)
    program = Column(String)
    category = Column(String, ForeignKey("category.name", onupdate="CASCADE"))
    placement = Column(String, ForeignKey("placement.name", onupdate="CASCADE"))
    instructor = Column(Integer, ForeignKey("instructor.id"))
    paid = Column(Boolean)
    place_limit = Column(Integer, nullable=True)
    registration_opens = Column(Integer, nullable=True)

    # category = relationship("Category", back_populates="classes")
    # placement = relationship("Placement", back_populates="classes")
    instructor_ = relationship("Instructor", back_populates="classes")
    schedule_records = relationship("ScheduleRecord", back_populates="class_")

    to_schema = class_to_schema


schedule_schema_record = Table(
    "schedule_schema_record",
    Base.metadata,
    Column("schedule_schema", ForeignKey("schedule_schema.id", ondelete="CASCADE"), primary_key=True),
    Column("schedule_record", ForeignKey("schedule_record.id", ondelete="CASCADE"), primary_key=True),
)


class ScheduleRecord(Base):
    __tablename__ = "schedule_record"

    id = Column(Integer, primary_key=True)
    week_day = Column(Integer)
    day_time = Column(Time)
    duration = Column(Integer)
    Class = Column(Integer, ForeignKey("class.id", ondelete="CASCADE"))

    class_ = relationship("Class", back_populates="schedule_records")

    to_schema = record_to_schema


class ScheduleSchema(Base):
    __tablename__ = "schedule_schema"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean, default=False)
    to_be_active_from = Column(DateTime(timezone=True), nullable=True)

    schedule_records = relationship("ScheduleRecord", secondary=schedule_schema_record)


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    credentials = Column(String)
    phone = Column(String, unique=True)
    additional_data = Column(JSON)


class BookedClasses(Base):
    __tablename__ = "booked_classes"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("class.id", ondelete="CASCADE"))
    date = Column(DateTime)


