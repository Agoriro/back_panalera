# Paso 12: src/infrastructure/database/repositories/user_repository.py
"""
Implementación del repositorio de User.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository as IUserRepository
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[UserModel], IUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id_user=model.id_user,
            user=model.user,
            password=model.password,
            id_role=model.id_role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id_user=entity.id_user,
            user=entity.user,
            password=entity.password,
            id_role=entity.id_role,
            is_active=entity.is_active,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        if not user.id_user:
            model.id_user = None
        created_model = await super().create(model)
        return self._to_entity(created_model)

    async def get_by_id(self, id_user: UUID) -> Optional[User]:
        model = await super().get_by_id(id_user)
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.user == username)
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[User]:
        models = await super().get_all()
        return [self._to_entity(m) for m in models]

    async def update(self, user: User) -> User:
        model = self._to_model(user)
        # SQLAlchemy merge para actualizar preservando session
        merged_model = await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(merged_model)
        return self._to_entity(merged_model)
