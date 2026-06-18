# Paso 8: src/domain/entities/role.py
"""
Entidad de dominio Role.
"""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Role:
    id_role: UUID
    name: str
