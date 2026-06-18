# Paso 14: src/application/dtos/movement_dto.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from src.domain.entities.movement import MovementType

class PurchaseCreate(BaseModel):
    id_supplier: UUID
    id_inventory: UUID
    quantity: int = Field(..., gt=0)
    value: Decimal = Field(..., gt=0) # unit price

class SaleCreate(BaseModel):
    id_inventory: UUID
    quantity: int = Field(..., gt=0)
    # value is calculated automatically

class MovementResponse(BaseModel):
    id_movement: UUID
    type_movement: MovementType
    date: datetime
    id_supplier: Optional[UUID]
    id_inventory: UUID
    quantity: int
    value: Decimal
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
