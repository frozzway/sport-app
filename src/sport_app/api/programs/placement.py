from fastapi import (
    APIRouter,
    Depends,
    status,
)

from ...models import Placement
from ...services import PlacementService
from ...services.auth import validate_admin_access


router = APIRouter(
    prefix='/placement',
    tags=['placements']
)


@router.get(
    '/',
    response_model=list[Placement]
)
def get_placements(
    placement_service: PlacementService = Depends()
):
    return placement_service.get_many()


@router.post(
    '/',
    response_model=Placement,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_admin_access)],
)
def create_placement(
    placement_data: Placement,
    placement_service: PlacementService = Depends()
):
    return placement_service.create_placement(placement_data)


@router.put(
    '/{placement_name}',
    response_model=Placement,
    dependencies=[Depends(validate_admin_access)],
)
def update_placement(
    placement_name: str,
    placement_data: Placement,
    placement_service: PlacementService = Depends()
):
    return placement_service.update_placement(placement_name, placement_data)


@router.delete(
    '/{placement_name}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_admin_access)],
)
def delete_placement(
    placement_name: str,
    placement_service: PlacementService = Depends()
):
    placement_service.delete_placement(placement_name)