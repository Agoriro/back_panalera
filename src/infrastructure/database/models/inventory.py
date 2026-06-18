# Paso 10: src/infrastructure/database/models/inventory.py
"""
Modelo SQLAlchemy para Inventory y InventoryPhotos.
"""
from sqlalchemy import Column, String, Boolean, text, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.infrastructure.database.models.base import Base

class InventoryModel(Base):
    __tablename__ = "inventory"

    id_inventory = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    description_inventory = Column(String, nullable=False)
    utility = Column(Numeric(18, 6), nullable=False)
    id_supplier = Column(UUID(as_uuid=True), ForeignKey("suppliers.id_supplier"), nullable=False)
    id_color = Column(UUID(as_uuid=True), ForeignKey("colors.id_color"), nullable=False)
    id_size = Column(UUID(as_uuid=True), ForeignKey("sizes.id_size"), nullable=False)
    id_category = Column(UUID(as_uuid=True), ForeignKey("categories.id_category"), nullable=False)
    id_gender = Column(UUID(as_uuid=True), ForeignKey("genders.id_gender"), nullable=False)
    is_active = Column(Boolean, default=True, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

    supplier = relationship("SupplierModel")
    color = relationship("ColorModel")
    size = relationship("SizeModel")
    category = relationship("CategoryModel")
    gender = relationship("GenderModel")
    photos = relationship("InventoryPhotoModel", back_populates="inventory", cascade="all, delete-orphan")


class InventoryPhotoModel(Base):
    __tablename__ = "inventory_photos"

    id_reg = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_inventory = Column(UUID(as_uuid=True), ForeignKey("inventory.id_inventory", ondelete="CASCADE"), nullable=False)
    url_photo = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

    inventory = relationship("InventoryModel", back_populates="photos")
