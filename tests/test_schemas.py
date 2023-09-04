import pytest
from unittest.mock import call
from dateutil import relativedelta as rd
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from sport_app import utils
from src.sport_app import services
from src.sport_app import tables
from src.sport_app.app import app
from .conftest import delete_all


client = TestClient(app)


@pytest.fixture()
def three_schemas(session_db):
    data = (
        ('schema1', True),
        ('schema2', False),
        ('schema3', False)
    )
    schemas = [tables.ScheduleSchema(name=name, active=active) for name, active in data]
    session_db.add_all(schemas)
    session_db.commit()
    yield schemas
    delete_all(session_db, schemas)

@pytest.fixture()
def next_week_schema(session_db):
    schema = tables.ScheduleSchema(name='schema-nw', to_be_active_from=utils.next_mo())
    session_db.add(schema)
    session_db.commit()
    yield schema
    delete_all(session_db, [schema])


@pytest.fixture()
def active_schema(session_db):
    schema = tables.ScheduleSchema(name='schema-name', active=True)
    session_db.add(schema)
    session_db.commit()
    yield schema
    delete_all(session_db, [schema])


@pytest.fixture()
def schema_with_records(session_db, active_schema, booked_rows_on_records):
    records = booked_rows_on_records[1]
    active_schema.records = records[::2]
    session_db.commit()
    return active_schema


def test_schema_activation(session_db, three_schemas):
    response = client.put(f'/api/schedule/schema/2', json={'active': True})
    old_active = session_db.query(tables.ScheduleSchema).filter_by(id=1).first()
    new_active = session_db.query(tables.ScheduleSchema).filter_by(id=2).first()
    assert response.status_code == 200
    assert old_active.active is False and new_active.active is True


def test_make_next_week_schema_active(session_db, three_schemas, next_week_schema):
    old_active = three_schemas[0]
    response = client.put(f'/api/schedule/schema/{next_week_schema.id}', json={'active': True})
    session_db.expire_all()

    assert response.status_code == 200
    assert old_active.active is False and next_week_schema.active is True
    assert next_week_schema.to_be_active_from is None


def test_include_records_in_schema(session_db, schema_with_records, records):
    records_to_include = [r.id for r in records[1::2]]
    session_db.query(tables.BookedClasses).all()

    response = client.post(f'/api/schedule/schema/{schema_with_records.id}/records', json=records_to_include)
    records_ids = [r.id for r in schema_with_records.records]

    assert response.status_code == 200
    assert all(rec in records_ids for rec in records_to_include)


def test_exclude_records_from_schema_removes_records(session_db, schema_with_records):
    records_to_exclude = [r.id for r in schema_with_records.records][::2]
    response = client.request('delete', f'/api/schedule/schema/{schema_with_records.id}/records', json=records_to_exclude)
    session_db.expire(schema_with_records)
    records_ids = [r.id for r in schema_with_records.records]

    assert response.status_code == 204
    assert all(rec not in records_ids for rec in records_to_exclude)


def test_excluding_records_from_schema_cancels_future_booking_on_active_schema(session_db, schema_with_records, mocker: MockerFixture):
    records = [r.id for r in schema_with_records.records]
    schema_service = services.SchemaService(session_db)

    method = mocker.patch.object(services.SchemaService, '_remove_booking', autospec=True)
    schema_service.exclude_records_from_schema_(schema_with_records.id, records)

    method.assert_has_calls([
     call(schema_service, records),
     call(schema_service, records, next_week=True)
    ])


def test_excluding_records_from_schema_cancels_future_booking_on_nw_schema(session_db, schema_with_records, mocker: MockerFixture):
    schema_with_records.to_be_active_from = utils.next_mo()
    schema_with_records.active = False
    session_db.commit()
    records = [r.id for r in schema_with_records.records]
    schema_service = services.SchemaService(session_db)

    method = mocker.patch.object(services.SchemaService, '_remove_booking', autospec=True)
    schema_service.exclude_records_from_schema_(schema_with_records.id, records)

    method.assert_called_once_with(schema_service, records, next_week=True)


def test_method_remove_book_rows(session_db, booked_rows):
    """ Tests the behaviour of SchemaService._remove_booked_rows"""
    schema_service = services.SchemaService(session_db)
    rows_to_remove = [(bk.program, bk.date) for bk in booked_rows[::2]]
    rows_ids = [bk.id for bk in booked_rows[::2]]

    schema_service._remove_booked_rows(rows_to_remove)

    assert  session_db.query(tables.BookedClasses)\
            .filter(tables.BookedClasses.id.in_(rows_ids))\
            .all() == []


@pytest.mark.parametrize('next_week', (False, True))
def test_method_remove_booking_on_records(session_db, booked_rows_on_records, next_week, mocker: MockerFixture):
    """ Tests the implementation of SchemaService._remove_booking"""
    booked_rows, records = booked_rows_on_records[0], booked_rows_on_records[1]
    interval = rd.relativedelta(days=7) if next_week else rd.relativedelta()
    expected = [(row.program, row.date + interval)
                for row in booked_rows
                if row.date + interval > utils.now()]
    schema_service = services.SchemaService(session_db)

    method = mocker.patch.object(services.SchemaService, '_remove_booked_rows', autospec=True)
    schema_service._remove_booking(records, next_week=next_week)

    method.assert_called_once_with(schema_service, expected)

