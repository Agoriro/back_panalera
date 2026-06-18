# Paso 8: src/domain/entities/movement.py
"""
Entidad de dominio Movement.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from decimal import Decimal

class MovementType(str, Enum):
    BUY = "Buy"
    SELL = "Sell"

@dataclass
class Movement:
    id_movement: UUID
    type_movement: MovementType
    date: datetime
    id_supplier: Optional[UUID]
    id_inventory: UUID
    quantity: int
    value: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
