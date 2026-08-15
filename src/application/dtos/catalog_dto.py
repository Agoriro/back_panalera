from pydantic import BaseModel, Field, ConfigDict, model_validator
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
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    name_category: Optional[str] = Field(None, min_length=1, max_length=50)
    name_color: Optional[str] = Field(None, min_length=1, max_length=50)
    name_size: Optional[str] = Field(None, min_length=1, max_length=50)
    name_gender: Optional[str] = Field(None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def check_at_least_one_name(self):
        val = self.name or self.name_category or self.name_color or self.name_size or self.name_gender
        if not val or not val.strip():
            raise ValueError("El nombre es requerido y no puede estar vacío")
        return self

    def get_name(self) -> str:
        return (self.name or self.name_category or self.name_color or self.name_size or self.name_gender or "").strip()

class BasicCatalogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    name_category: Optional[str] = Field(None, min_length=1, max_length=50)
    name_color: Optional[str] = Field(None, min_length=1, max_length=50)
    name_size: Optional[str] = Field(None, min_length=1, max_length=50)
    name_gender: Optional[str] = Field(None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def check_at_least_one_name(self):
        val = self.name or self.name_category or self.name_color or self.name_size or self.name_gender
        if not val or not val.strip():
            raise ValueError("El nombre es requerido y no puede estar vacío")
        return self

    def get_name(self) -> str:
        return (self.name or self.name_category or self.name_color or self.name_size or self.name_gender or "").strip()

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
