# Paso 8: src/domain/entities/user.py
"""
Entidad de dominio User.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    id_user: UUID
    user: str
    password: str
    id_role: UUID
    is_active: bool
    role_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
