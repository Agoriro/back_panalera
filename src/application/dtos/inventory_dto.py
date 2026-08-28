# Paso 14: src/application/dtos/inventory_dto.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

MAX_INVENTORY_PHOTOS = 10


class InventoryPhotoCreate(BaseModel):
    url_photos: list[AnyHttpUrl] = Field(
        ..., min_length=1, max_length=MAX_INVENTORY_PHOTOS
    )

    @field_validator("url_photos")
    @classmethod
    def validate_photo_urls(cls, urls: list[AnyHttpUrl]) -> list[AnyHttpUrl]:
        if any(len(str(url)) > 2048 for url in urls):
            raise ValueError("Cada URL debe tener máximo 2048 caracteres")
        if len({str(url) for url in urls}) != len(urls):
            raise ValueError("No se permiten URLs de fotos duplicadas")
        return urls


class InventoryPhotoResponse(BaseModel):
    id_reg: UUID
    id_inventory: UUID
    url_photo: str
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class InventoryCreate(BaseModel):
    description_inventory: str = Field(..., min_length=1, max_length=255)
    code_inventory: str | None = Field(
        None, max_length=100, description="Código de producto (SKU)"
    )
    barcode_inventory: str | None = Field(
        None, max_length=100, description="Código de barras del producto"
    )
    utility: Decimal = Field(..., ge=0)
    id_supplier: UUID
    id_color: UUID
    id_size: UUID
    id_category: UUID
    id_gender: UUID

    @field_validator("description_inventory", mode="before")
    @classmethod
    def strip_description(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("code_inventory", "barcode_inventory", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class InventoryUpdate(BaseModel):
    description_inventory: str | None = Field(None, min_length=1, max_length=255)
    code_inventory: str | None = Field(None, max_length=100)
    barcode_inventory: str | None = Field(None, max_length=100)
    utility: Decimal | None = Field(None, ge=0)
    id_supplier: UUID | None = None
    id_color: UUID | None = None
    id_size: UUID | None = None
    id_category: UUID | None = None
    id_gender: UUID | None = None

    @field_validator("description_inventory", mode="before")
    @classmethod
    def strip_description(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("code_inventory", "barcode_inventory", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


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
