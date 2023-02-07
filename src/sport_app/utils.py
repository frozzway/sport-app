from dateutil.utils import today as _today
from dateutil.tz import gettz
from dateutil import relativedelta as rd
import datetime
from sqlalchemy import func, Integer, Time
from sqlalchemy.sql.expression import BinaryExpression

from .settings import settings

tz = gettz(settings.timezone)


def today() -> datetime.datetime:
    return _today(tz)


def now() -> datetime.datetime:
    return datetime.datetime.now(tz)


def next_mo() -> datetime.datetime:
    """Возвращает понедельник на следующей неделе Aware"""
    TODAY = today()
    return TODAY + rd.relativedelta(days=+1, weekday=rd.MO)


def this_mo() -> datetime.datetime:
    """Возвращает понедельник на текущей неделе Aware"""
    TODAY = today()
    return TODAY + rd.relativedelta(weekday=rd.MO(-1))


def this_mo_sql() -> BinaryExpression:
    """Возвращает понедельник на текущей неделе NotAware [SQL BinaryExpression]"""
    return func.current_date() + 1 - func.cast(func.extract("isodow", func.current_date()), Integer)


def previous_mo_sql():
    """Возвращает понедельник на предыдущей неделе NotAware [SQL BinaryExpression]"""
    return this_mo_sql() - 7


def calc_date_sql(week_day: Integer, day_time: Time):
    """Конструирует дату по дню недели и времени дня на текущей неделе type::timestamp [SQL BinaryExpression]"""
    MONDAY = this_mo_sql()
    return MONDAY + week_day + day_time


def make_interval(years=0, months=0, weeks=0, days=0):
    """Возвращает объект type::interval"""
    return func.make_interval(years, months, weeks, days)


def tz_date_sql(date):
    """Переводит date::timestamp в date::timestamptz"""
    return func.timezone(settings.timezone, date)


def calculate_date(week_day: int, day_time: datetime.time) -> datetime.datetime:
    """Конструирует дату по дню недели и времени дня на текущей неделе Aware"""
    MONDAY = this_mo()
    return MONDAY + rd.relativedelta(days=+week_day, hour=day_time.hour, minute=day_time.minute)