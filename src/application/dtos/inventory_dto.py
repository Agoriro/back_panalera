# Paso 14: src/application/dtos/inventory_dto.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class InventoryPhotoCreate(BaseModel):
    url_photos: List[str] = Field(..., min_length=1)

class InventoryPhotoResponse(BaseModel):
    id_reg: UUID
    id_inventory: UUID
    url_photo: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class InventoryCreate(BaseModel):
    description_inventory: str = Field(..., min_length=1)
    utility: Decimal = Field(..., ge=0)
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID

class InventoryUpdate(BaseModel):
    description_inventory: Optional[str] = Field(None, min_length=1)
    utility: Optional[Decimal] = Field(None, ge=0)
    id_supplier: Optional[UUID] = None
    id_color: Optional[UUID] = None
    id_size: Optional[UUID] = None
    id_category: Optional[UUID] = None
    id_gender: Optional[UUID] = None

class InventoryResponse(BaseModel):
    id_inventory: UUID
    description_inventory: str
    utility: Decimal
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    photos: Optional[List[InventoryPhotoResponse]] = None

    model_config = ConfigDict(from_attributes=True)
