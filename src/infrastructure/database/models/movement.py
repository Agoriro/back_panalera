# Paso 10: src/infrastructure/database/models/movement.py
"""
Modelo SQLAlchemy para Movement.
"""
from sqlalchemy import Column, Integer, text, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.infrastructure.database.models.base import Base
from src.domain.entities.movement import MovementType

class MovementModel(Base):
    __tablename__ = "movements"

    id_movement = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    type_movement = Column(Enum(MovementType), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    id_supplier = Column(UUID(as_uuid=True), ForeignKey("suppliers.id_supplier"), nullable=True)
    id_inventory = Column(UUID(as_uuid=True), ForeignKey("inventory.id_inventory"), nullable=False)
    quantity = Column(Integer, nullable=False)
    value = Column(Numeric(18, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

    supplier = relationship("SupplierModel")
    inventory = relationship("InventoryModel")
