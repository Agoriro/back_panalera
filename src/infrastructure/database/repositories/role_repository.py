# Paso 12: src/infrastructure/database/repositories/role_repository.py
"""
Implementación del repositorio de Role.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.role import Role
from src.domain.repositories.role_repository import RoleRepository as IRoleRepository
from src.infrastructure.database.models.role import RoleModel
from src.infrastructure.database.repositories.base_repository import BaseRepository

class RoleRepository(BaseRepository[RoleModel], IRoleRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(RoleModel, session)

    def _to_entity(self, model: RoleModel) -> Role:
        return Role(id_role=model.id_role, name=model.name)

    def _to_model(self, entity: Role) -> RoleModel:
        return RoleModel(id_role=entity.id_role, name=entity.name)

    async def create(self, role: Role) -> Role:
        model = self._to_model(role)
        # Evitamos mandar id nulo para que la DB genere el UUID
        if not role.id_role:
            model.id_role = None
        created_model = await super().create(model)
        return self._to_entity(created_model)

    async def get_by_id(self, id_role: UUID) -> Optional[Role]:
        model = await super().get_by_id(id_role)
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[Role]:
        models = await super().get_all()
        return [self._to_entity(m) for m in models]

    async def update(self, role: Role) -> Role:
        model = self._to_model(role)
        updated_model = await super().update(model)
        return self._to_entity(updated_model)
