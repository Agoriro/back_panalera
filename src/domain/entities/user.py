# Paso 8: src/domain/entities/user.py
"""
Entidad de dominio User.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class User:
    id_user: UUID
    user: str
    password: str
    id_role: UUID
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
