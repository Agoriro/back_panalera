# Paso 10: src/infrastructure/database/models/catalog.py
"""
Modelos SQLAlchemy para el catálogo (Supplier, Color, Size, Category, Gender).
"""
from sqlalchemy import Column, String, Boolean, text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database.models.base import Base

class SupplierModel(Base):
    __tablename__ = "suppliers"

    id_supplier = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name_supplier = Column(String, nullable=False)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

class ColorModel(Base):
    __tablename__ = "colors"

    id_color = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name_color = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

class SizeModel(Base):
    __tablename__ = "sizes"

    id_size = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name_size = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

class CategoryModel(Base):
    __tablename__ = "categories"

    id_category = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name_category = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

class GenderModel(Base):
    __tablename__ = "genders"

    id_gender = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name_gender = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))
