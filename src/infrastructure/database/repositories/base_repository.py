# Paso 12: src/infrastructure/database/repositories/base_repository.py
"""
Repositorio base con operaciones CRUD comunes utilizando SQLAlchemy AsyncSession.
"""
from typing import Type, TypeVar, Generic, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        pk_column = self.model.__mapper__.primary_key[0]
        query = select(self.model).where(pk_column == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[ModelType]:
        query = select(self.model)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in

    async def update(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in
