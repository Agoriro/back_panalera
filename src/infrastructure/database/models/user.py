# Paso 10: src/infrastructure/database/models/user.py
"""
Modelo SQLAlchemy para User.
"""
from sqlalchemy import Column, String, Boolean, text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.infrastructure.database.models.base import Base

class UserModel(Base):
    __tablename__ = "users"

    id_user = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    id_role = Column(UUID(as_uuid=True), ForeignKey("roles.id_role"), nullable=False)
    is_active = Column(Boolean, default=True, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("now()"))

    role = relationship("RoleModel")
