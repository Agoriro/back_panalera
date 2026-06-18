# Paso 14: src/application/dtos/catalog_dto.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class SupplierBase(BaseModel):
    name_supplier: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id_supplier: UUID
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class BasicCatalogCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class BasicCatalogUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class ColorResponse(BaseModel):
    id_color: UUID
    name_color: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class SizeResponse(BaseModel):
    id_size: UUID
    name_size: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id_category: UUID
    name_category: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class GenderResponse(BaseModel):
    id_gender: UUID
    name_gender: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
