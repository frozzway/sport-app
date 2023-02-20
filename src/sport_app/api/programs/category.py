from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...models import Category
from ...services import CategoryService
from ...services.auth import validate_admin_access


router = APIRouter(
    prefix='/category',
    tags=['categories'],
)


@router.get(
    '/',
    response_model=list[Category]
)
def get_categories(
    category_service: CategoryService = Depends()
):
    return category_service.get_many()


@router.post(
    '/',
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_admin_access)],
)
def create_category(
    category_data: Category,
    category_service: CategoryService = Depends()
):
    return category_service.create_category(category_data)


@router.put(
    '/{category_name}',
    response_model=Category,
    dependencies=[Depends(validate_admin_access)],
)
def update_category(
    category_name: str,
    category_data: Category,
    category_service: CategoryService = Depends()
):
    return category_service.update_category(category_name, category_data)


@router.delete(
    '/{category_name}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_admin_access)],
)
def delete_category(
    category_name: str,
    category_service: CategoryService = Depends()
):
    category_service.delete_category(category_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
