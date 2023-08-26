import datetime
import itertools
from typing import Iterable

import pytest
from dateutil import relativedelta as rd

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session

from sport_app.settings import settings
from src.sport_app.tables import Base
from src.sport_app.app import app
from src.sport_app.database import get_session
from src.sport_app import tables
from src.sport_app.services.auth import validate_admin_access


url_object = URL.create(
    'postgresql',
    username='admin',
    password='123',
    host='localhost',
    port=5432,
    database='test_sport_app',
)
engine = create_engine(url_object)


def empty_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def delete_all(session: Session, instances: Iterable):
    for i in instances:
        session.delete(i)
    session.commit()


@pytest.fixture(scope="session")
def sessionmaker_db():
    empty_db()
    Session = sessionmaker(
        engine,
        autocommit=False,
        autoflush=False,
    )
    return Session


@pytest.fixture(scope="session")
def session_db(sessionmaker_db):
    session = sessionmaker_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session", autouse=True)
def session_db_dependency(session_db):
    def get_session_test_db():
        yield session_db

    app.dependency_overrides[get_session] = get_session_test_db


@pytest.fixture(scope="session", autouse=True)
def admin_access(session_db):
    staff = tables.Staff(username='John Doe', email='email@mail.cm', role='admin', password_hash='123')
    session_db.add(staff)
    session_db.commit()

    def override():
        return staff

    app.dependency_overrides[validate_admin_access] = override


@pytest.fixture(name='instructor')
def instructor_no_image(session_db):
    instructor = tables.Instructor(
        credentials='instructor-name',
        phone='900'
    )
    session_db.add(instructor)
    session_db.commit()
    yield instructor
    delete_all(session_db, [instructor])


@pytest.fixture(name='instructor_with_image')
def instructor_with_image(session_db, tmp_path, instructor):
    token = 'token_to_delete'
    instructor.photo_token = token
    path = (tmp_path / settings.images_path / 'instructors')
    path.mkdir(parents=True)
    (path / f'{token}.jpg').touch()
    session_db.commit()
    yield instructor
    delete_all(session_db, [instructor])


@pytest.fixture()
def categories(session_db):
    categories = [tables.Category(name=f'category{i}') for i in range(3)]
    session_db.add_all(categories)
    session_db.commit()
    yield categories
    delete_all(session_db, categories)


@pytest.fixture()
def placements(session_db):
    placements = [tables.Placement(name=f'placement{i}') for i in range(3)]
    session_db.add_all(placements)
    session_db.commit()
    yield placements
    delete_all(session_db, placements)


@pytest.fixture()
def programs(session_db, categories, placements, instructor):
    programs = [
        tables.Program(
            name=f'program{num+1}',
            category=category.name,
            placement=placement.name,
            instructor=instructor.id,
            paid=False,
            available_registration=True
        )
        for num, (category, placement)
        in enumerate(itertools.product(categories, placements))
    ]
    session_db.add_all(programs)
    session_db.commit()
    yield programs
    delete_all(session_db, programs)


@pytest.fixture()
def records(session_db, programs):
    records = []
    for day in range(7):
        for hour, program in zip(range(11, 20), programs):
            records.append(tables.SchemaRecord(
                week_day=day,
                day_time=datetime.time(hour),
                duration=60,
                program=program.id
            ))
    session_db.add_all(records)
    session_db.commit()
    yield records
    delete_all(session_db, records)


@pytest.fixture()
def client(session_db):
    client = tables.Client(credentials='client-credentials', phone='123')
    session_db.add(client)
    session_db.commit()
    yield client
    delete_all(session_db, [client])


@pytest.fixture()
def booked_rows(session_db, programs, client):
    """ Some rows on BookedClasses with future dates for each program"""
    rows = [
        tables.BookedClasses(
            client=client.id,
            program=program.id,
            date=datetime.datetime.utcnow() + rd.relativedelta(days=+1)
        )
        for program in programs
    ]
    session_db.add_all(rows)
    session_db.commit()
    yield rows
    delete_all(session_db, rows)


@pytest.fixture()
def booked_rows_on_records(session_db, records, client):
    """ Rows on tables.BookedClasses that correspond to Records """
    rows = [
        tables.BookedClasses(
            client=client.id,
            program=record.program,
            date=record.date
        )
        for record in records
    ]
    session_db.add_all(rows)
    session_db.commit()
    yield rows, records
    rows = session_db.query(tables.BookedClasses).all()
    delete_all(session_db, rows)