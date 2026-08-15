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
    id_supplier: Optional[UUID] = None
    name_supplier: str = ""
    address: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Color:
    id_color: Optional[UUID] = None
    name_color: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Size:
    id_size: Optional[UUID] = None
    name_size: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Category:
    id_category: Optional[UUID] = None
    name_category: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Gender:
    id_gender: Optional[UUID] = None
    name_gender: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
