from fastapi import (
    Depends,
)
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from sqlalchemy.orm import aliased

from ..database import get_session
from .. import (
    tables,
    models,
    utils
)


class ReportsService:
    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        self.session = session

    def client_report(self, client_id: int, period: models.Periods) -> list[models.ClientReportRow]:
        """Отчёт о видах и количестве посещенных занятиях клиентом в динамике"""
        BC = tables.BookedClasses

        rows = self.session.execute(
            select(
                func.extract("year", BC.date).label("year"),
                func.extract(period.name, BC.date).label("period"),
                func.count(BC.id),
                tables.Program
            )
            .join(BC)
            .where(BC.client == client_id)
            .group_by("year", "period", tables.Program)
            .order_by(tables.Program.id, desc("year"), desc("period"))
        ).all()

        response = {}
        for row in rows:
            program = row[3]
            period_begin, period_end = self.calc_periods(period, row)
            if not response.get(program):
                response[program] = []
            response[program].append(models.ProgramsReportRow(
                period_begin=period_begin,
                period_end=period_end,
                period_num=int(row.period),
                amount=row.count
            ))

        return [models.ClientReportRow(program=program.to_model(), data=data) for program, data in response.items()]

    @staticmethod
    def calc_periods(period: models.Periods, row):
        period_begin, period_end = None, None
        if period == models.Periods.week:
            period_begin = utils.mo_on_week(row.year, row.period)
            period_end = utils.su_on_week(row.year, row.period)
        elif period == models.Periods.month:
            period_begin = utils.first_month_day(row.year, row.period)
            period_end = utils.last_month_day(row.year, row.period)
        return period_begin, period_end

    def programs_report(self, req: models.ProgramsReport) -> models.ProgramsReportResponse:
        """Отчет о количестве и динамике изменений посещаемости занятия или группы занятий по неделям/месяцам"""
        BC = tables.BookedClasses
        subq = (
            select(BC.date, func.count(BC.id))
            .where(BC.program.in_(req.programs))
            .group_by(BC.date)
            .subquery()
        )
        rows = self.session.execute(
            select(
                func.extract(req.period.name, subq.c.date).label("period"),
                func.extract("year", subq.c.date).label("year"),
                func.sum(subq.c.count)
            )
            .group_by("year", "period")
            .order_by(desc("year"), desc("period"))
        ).all()

        data = []
        for row in rows:
            period_begin, period_end = self.calc_periods(req.period, row)
            data.append(models.ProgramsReportRow(
                period_begin=period_begin,
                period_end=period_end,
                period_num=int(row.period),
                amount=row.sum
            ))
        return models.ProgramsReportResponse(
            programs=req.programs,
            period=req.period,
            data=data
        )
