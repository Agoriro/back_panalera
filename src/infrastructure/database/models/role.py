# Paso 10: src/infrastructure/database/models/role.py
"""
Modelo SQLAlchemy para Role.
"""
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database.models.base import Base

class RoleModel(Base):
    __tablename__ = "roles"

    id_role = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False, unique=True)
