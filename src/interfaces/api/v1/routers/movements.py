# Paso 16: src/interfaces/api/v1/routers/movements.py
from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.application.dtos.movement_dto import PurchaseCreate, SaleCreate, MovementResponse
from src.application.use_cases.movement_use_case import MovementUseCase
from src.domain.entities.movement import MovementType
from src.interfaces.api.dependencies.use_cases import get_movement_use_case
from src.interfaces.api.dependencies.auth import is_authenticated

router = APIRouter(prefix="/movements", tags=["Movements"], dependencies=[Depends(is_authenticated)])

@router.post("/purchase", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def register_purchase(data: PurchaseCreate, use_case: MovementUseCase = Depends(get_movement_use_case)):
    return await use_case.register_purchase(data)

@router.post("/sale", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def register_sale(data: SaleCreate, use_case: MovementUseCase = Depends(get_movement_use_case)):
    return await use_case.register_sale(data)

@router.get("", response_model=List[MovementResponse])
async def get_movements(
    type: Optional[MovementType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    id_inventory: Optional[UUID] = None,
    use_case: MovementUseCase = Depends(get_movement_use_case)
):
    return await use_case.get_all(type, date_from, date_to, id_inventory)
