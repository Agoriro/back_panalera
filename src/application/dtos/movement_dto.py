# Paso 14: src/application/dtos/movement_dto.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.movement import MovementType


class PurchaseCreate(BaseModel):
    id_supplier: UUID
    id_inventory: UUID
    quantity: int = Field(..., gt=0)
    value: Decimal = Field(..., gt=0)  # unit price


class SaleCreate(BaseModel):
    id_inventory: UUID
    quantity: int = Field(..., gt=0)
    # value is calculated automatically


class MovementResponse(BaseModel):
    id_movement: UUID
    type_movement: MovementType
    date: datetime
    id_supplier: UUID | None
    id_inventory: UUID
    quantity: int
    value: Decimal
    unit_cost: Decimal
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
