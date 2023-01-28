from fastapi import (
    APIRouter,
    Depends,
    status,
    Response
)

from ...schemas import Category
from ...services import CategoryService


router = APIRouter(
    prefix='/category',
    tags=['Категории']
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
)
def create_category(
    category_data: Category,
    category_service: CategoryService = Depends()
):
    return category_service.create(category_data)


@router.put(
    '/{category_name}',
    response_model=Category
)
def update_category(
    category_name: str,
    category_data: Category,
    category_service: CategoryService = Depends()
):
    return category_service.update(category_name, category_data)


@router.delete(
    '/{category_name}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_name: str,
    category_service: CategoryService = Depends()
):
    category_service.delete(category_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
