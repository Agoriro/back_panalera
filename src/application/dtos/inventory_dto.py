# Paso 14: src/application/dtos/inventory_dto.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryPhotoCreate(BaseModel):
    url_photos: list[str] = Field(..., min_length=1)


class InventoryPhotoResponse(BaseModel):
    id_reg: UUID
    id_inventory: UUID
    url_photo: str
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class InventoryCreate(BaseModel):
    description_inventory: str = Field(..., min_length=1)
    code_inventory: str | None = Field(None, description="Código de producto (SKU)")
    barcode_inventory: str | None = Field(
        None, description="Código de barras del producto"
    )
    utility: Decimal = Field(..., ge=0)
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID


class InventoryUpdate(BaseModel):
    description_inventory: str | None = Field(None, min_length=1)
    code_inventory: str | None = None
    barcode_inventory: str | None = None
    utility: Decimal | None = Field(None, ge=0)
    id_supplier: UUID | None = None
    id_color: UUID | None = None
    id_size: UUID | None = None
    id_category: UUID | None = None
    id_gender: UUID | None = None


class InventoryResponse(BaseModel):
    id_inventory: UUID
    description_inventory: str
    code_inventory: str | None = None
    barcode_inventory: str | None = None
    utility: Decimal
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
    photos: list[InventoryPhotoResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
