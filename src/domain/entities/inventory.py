# Paso 8: src/domain/entities/inventory.py
"""
Entidad de dominio Inventory y InventoryPhoto.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

@dataclass
class InventoryPhoto:
    id_reg: UUID
    id_inventory: UUID
    url_photo: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Inventory:
    id_inventory: UUID
    description_inventory: str
    utility: Decimal
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Campo opcional para almacenar las fotos asociadas al recuperar el inventario
    photos: Optional[list[InventoryPhoto]] = None
