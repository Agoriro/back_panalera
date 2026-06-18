# Paso 8: src/domain/entities/catalog.py
"""
Entidades de dominio del catálogo (Supplier, Color, Size, Category, Gender).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Supplier:
    id_supplier: UUID
    name_supplier: str
    address: Optional[str]
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Color:
    id_color: UUID
    name_color: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Size:
    id_size: UUID
    name_size: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Category:
    id_category: UUID
    name_category: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Gender:
    id_gender: UUID
    name_gender: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
