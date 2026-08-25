# Paso 8: src/domain/entities/catalog.py
"""
Entidades de dominio del catálogo (Supplier, Color, Size, Category, Gender).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Supplier:
    id_supplier: UUID | None = None
    name_supplier: str = ""
    address: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Color:
    id_color: UUID | None = None
    name_color: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Size:
    id_size: UUID | None = None
    name_size: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Category:
    id_category: UUID | None = None
    name_category: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Gender:
    id_gender: UUID | None = None
    name_gender: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
