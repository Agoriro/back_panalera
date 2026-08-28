# Paso 8: src/domain/entities/inventory.py
"""
Entidad de dominio Inventory y InventoryPhoto.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class InventoryPhoto:
    id_reg: UUID
    id_inventory: UUID
    url_photo: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
    code_inventory: str | None = None
    barcode_inventory: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # Campo opcional para almacenar las fotos asociadas al recuperar el inventario
    photos: list[InventoryPhoto] | None = None
