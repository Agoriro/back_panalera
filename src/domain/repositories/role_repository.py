# Paso 9: src/domain/repositories/role_repository.py
"""
Interfaz de repositorio para la entidad Role.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.entities.role import Role

class RoleRepository(ABC):
    @abstractmethod
    async def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    async def get_by_id(self, id_role: UUID) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Role]:
        pass

    @abstractmethod
    async def update(self, role: Role) -> Role:
        pass
