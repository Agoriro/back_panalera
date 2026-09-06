# Paso 16: src/interfaces/api/v1/routers/movements.py
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.movement_dto import (
    MovementResponse,
    MovementUpdate,
    PurchaseCreate,
    SaleCreate,
)
from src.application.dtos.pagination_dto import Page
from src.application.use_cases.movement_use_case import MovementUseCase
from src.domain.entities.movement import MovementType
from src.interfaces.api.dependencies.auth import Permission, has_permission
from src.interfaces.api.dependencies.use_cases import get_movement_use_case

router = APIRouter(
    prefix="/movements",
    tags=["Movements"],
    dependencies=[Depends(has_permission(Permission.READ_DATA))],
)


@router.post(
    "/purchase",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.WRITE_MOVEMENTS))],
)
async def register_purchase(
    data: PurchaseCreate, use_case: MovementUseCase = Depends(get_movement_use_case)
):
    return await use_case.register_purchase(data)


@router.post(
    "/sale",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.WRITE_MOVEMENTS))],
)
async def register_sale(
    data: SaleCreate, use_case: MovementUseCase = Depends(get_movement_use_case)
):
    return await use_case.register_sale(data)


@router.put(
    "/{id_movement}",
    response_model=MovementResponse,
    dependencies=[Depends(has_permission(Permission.WRITE_MOVEMENTS))],
)
async def update_movement(
    id_movement: UUID,
    data: MovementUpdate,
    use_case: MovementUseCase = Depends(get_movement_use_case),
):
    return await use_case.update(id_movement, data)


@router.get("", response_model=Page[MovementResponse])
async def get_movements(
    type: MovementType | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    id_inventory: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    use_case: MovementUseCase = Depends(get_movement_use_case),
):
    return await use_case.get_all(
        type, date_from, date_to, id_inventory, page, page_size
    )
