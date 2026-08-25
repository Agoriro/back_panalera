# Paso 8: src/domain/entities/movement.py
"""
Entidad de dominio Movement.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class MovementType(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


@dataclass
class Movement:
    id_movement: UUID
    type_movement: MovementType
    date: datetime
    id_supplier: UUID | None
    id_inventory: UUID
    quantity: int
    value: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None
