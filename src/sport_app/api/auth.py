from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm

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
    '/sign-up',
    response_model=Token,
    dependencies=[Depends(validate_admin_access)],
    description='Регистрация сотрудника'
)
def sign_up(
    staff_data: StaffCreate,
    auth_service: AuthService = Depends(),
):
    return auth_service.register_new_staff(staff_data)