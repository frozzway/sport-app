from fastapi import (
    APIRouter,
    Depends,
)
from ..models import ClientReport, ProgramsReportResponse, ProgramsReport
from ..services.auth import validate_admin_access, validate_operator_access
from ..services.reports import ReportsService


router = APIRouter(
    prefix='/reports',
    tags=['reports']
)


@router.get(
    '/client/{client_id}',
    response_model=list[ClientReport],
    dependencies=[Depends(validate_admin_access)],
)
def get_client_report(
    client_id: int,
    report_service: ReportsService = Depends()
):
    return report_service.client_report(client_id)


@router.post(
    '/programs',
    response_model=ProgramsReportResponse,
    dependencies=[Depends(validate_admin_access)]
)
def get_programs_report(
    report_data: ProgramsReport,
    report_service: ReportsService = Depends(),
):
    return report_service.programs_report(report_data)

