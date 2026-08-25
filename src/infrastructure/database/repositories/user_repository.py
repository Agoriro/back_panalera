# Paso 12: src/infrastructure/database/repositories/user_repository.py
"""
Implementación del repositorio de User.
"""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
            token_version=model.token_version,
            role_name=model.role.name if getattr(model, "role", None) else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id_user=entity.id_user,
            user=entity.user,
            password=entity.password,
            id_role=entity.id_role,
            is_active=entity.is_active,
            token_version=entity.token_version,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        if not user.id_user:
            model.id_user = None
        created_model = await super().create(model)
        # Recargar con el rol cargado
        query = (
            select(UserModel)
            .options(joinedload(UserModel.role))
            .where(UserModel.id_user == created_model.id_user)
        )
        result = await self.session.execute(query)
        created_model = result.scalars().first()
        return self._to_entity(created_model)  # type: ignore

    async def get_by_id(self, id_user: UUID) -> User | None:
        query = (
            select(UserModel)
            .options(joinedload(UserModel.role))
            .where(UserModel.id_user == id_user)
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        query = (
            select(UserModel)
            .options(joinedload(UserModel.role))
            .where(UserModel.user == username)
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[User]:
        query = select(UserModel).options(joinedload(UserModel.role))
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, user: User) -> User:
        model = self._to_model(user)
        # SQLAlchemy merge para actualizar preservando session
        merged_model = await self.session.merge(model)
        await self.session.commit()
        # Recargar con el rol cargado
        query = (
            select(UserModel)
            .options(joinedload(UserModel.role))
            .where(UserModel.id_user == merged_model.id_user)
        )
        result = await self.session.execute(query)
        merged_model = result.scalars().first()
        return self._to_entity(merged_model)  # type: ignore

    async def rotate_token_version(
        self, id_user: UUID, expected_version: int
    ) -> User | None:
        statement = (
            update(UserModel)
            .where(UserModel.id_user == id_user)
            .where(UserModel.token_version == expected_version)
            .where(UserModel.is_active.is_(True))
            .values(token_version=UserModel.token_version + 1)
        )
        result = await self.session.execute(statement)
        if result.rowcount != 1:
            await self.session.rollback()
            return None
        await self.session.commit()
        return await self.get_by_id(id_user)
