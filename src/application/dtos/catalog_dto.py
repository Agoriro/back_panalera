from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class SupplierBase(BaseModel):
    name_supplier: str = Field(..., min_length=1, max_length=100)
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id_supplier: UUID
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    @property
    def id(self) -> UUID:
        return self.id_supplier

    @computed_field
    @property
    def name(self) -> str:
        return self.name_supplier

    model_config = ConfigDict(from_attributes=True)


class BasicCatalogCreate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    name_category: str | None = Field(None, min_length=1, max_length=50)
    name_color: str | None = Field(None, min_length=1, max_length=50)
    name_size: str | None = Field(None, min_length=1, max_length=50)
    name_gender: str | None = Field(None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def check_at_least_one_name(self):
        val = (
            self.name
            or self.name_category
            or self.name_color
            or self.name_size
            or self.name_gender
        )
        if not val or not val.strip():
            raise ValueError("El nombre es requerido y no puede estar vacío")
        return self

    def get_name(self) -> str:
        return (
            self.name
            or self.name_category
            or self.name_color
            or self.name_size
            or self.name_gender
            or ""
        ).strip()


class BasicCatalogUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    name_category: str | None = Field(None, min_length=1, max_length=50)
    name_color: str | None = Field(None, min_length=1, max_length=50)
    name_size: str | None = Field(None, min_length=1, max_length=50)
    name_gender: str | None = Field(None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def check_at_least_one_name(self):
        val = (
            self.name
            or self.name_category
            or self.name_color
            or self.name_size
            or self.name_gender
        )
        if not val or not val.strip():
            raise ValueError("El nombre es requerido y no puede estar vacío")
        return self

    def get_name(self) -> str:
        return (
            self.name
            or self.name_category
            or self.name_color
            or self.name_size
            or self.name_gender
            or ""
        ).strip()


class ColorResponse(BaseModel):
    id_color: UUID
    name_color: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    @property
    def id(self) -> UUID:
        return self.id_color

    @computed_field
    @property
    def name(self) -> str:
        return self.name_color

    model_config = ConfigDict(from_attributes=True)


class SizeResponse(BaseModel):
    id_size: UUID
    name_size: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    @property
    def id(self) -> UUID:
        return self.id_size

    @computed_field
    @property
    def name(self) -> str:
        return self.name_size

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id_category: UUID
    name_category: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    @property
    def id(self) -> UUID:
        return self.id_category

    @computed_field
    @property
    def name(self) -> str:
        return self.name_category

    model_config = ConfigDict(from_attributes=True)


class GenderResponse(BaseModel):
    id_gender: UUID
    name_gender: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    @property
    def id(self) -> UUID:
        return self.id_gender

    @computed_field
    @property
    def name(self) -> str:
        return self.name_gender

    model_config = ConfigDict(from_attributes=True)
