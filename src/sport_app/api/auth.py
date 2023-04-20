from fastapi import (
    APIRouter,
    Depends,
    status
)
from fastapi.security import OAuth2PasswordRequestForm

from ..models import Staff
from ..models import Token, StaffCreate
from ..services import AuthService
from ..services.auth import validate_admin_access


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post(
    '/sign-in',
    response_model=Token
)
def sign_in(
    auth_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    return auth_service.authenticate_staff(auth_data.username, auth_data.password)


@router.post(
    '/staff/sign-up',
    response_model=Staff,
    dependencies=[Depends(validate_admin_access)],
    description='Регистрация сотрудника'
)
def sign_up(
    staff_data: StaffCreate,
    auth_service: AuthService = Depends(),
):
    return auth_service.register_new_staff(staff_data)


@router.get(
    '/staff',
    response_model=list[Staff],
    dependencies=[Depends(validate_admin_access)],
)
def get_all_staff(
    auth_service: AuthService = Depends(),
):
    return auth_service.get_all_staff()


@router.delete(
    '/staff/{staff_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_admin_access)],
)
def delete_staff(
    staff_id: int,
    auth_service: AuthService = Depends(),
):
    auth_service.delete_staff(staff_id)