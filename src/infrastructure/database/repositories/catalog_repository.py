# Paso 12: src/infrastructure/database/repositories/catalog_repository.py
"""
Implementación de repositorios de catálogo.
"""

from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.catalog import Category, Color, Gender, Size, Supplier
from src.domain.repositories.catalog_repository import BaseCatalogRepository
from src.domain.repositories.catalog_repository import (
    CategoryRepository as ICategoryRepository,
)
from src.domain.repositories.catalog_repository import (
    ColorRepository as IColorRepository,
)
from src.domain.repositories.catalog_repository import (
    GenderRepository as IGenderRepository,
)
from src.domain.repositories.catalog_repository import SizeRepository as ISizeRepository
from src.domain.repositories.catalog_repository import (
    SupplierRepository as ISupplierRepository,
)
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.catalog import (
    CategoryModel,
    ColorModel,
    GenderModel,
    SizeModel,
    SupplierModel,
)
from src.infrastructure.database.repositories.base_repository import BaseRepository

T_Entity = TypeVar("T_Entity")
T_Model = TypeVar("T_Model", bound=Base)


class SQLAlchemyCatalogRepository(
    BaseRepository[T_Model], BaseCatalogRepository[T_Entity]
):
    def __init__(
        self,
        model_cls: type[T_Model],
        entity_cls: type[T_Entity],
        session: AsyncSession,
    ):
        super().__init__(model_cls, session)
        self.entity_cls = entity_cls

    def _to_entity(self, model: T_Model) -> T_Entity:
        # Crea entidad dinámicamente mapeando los atributos
        return self.entity_cls(
            **{c.name: getattr(model, c.name) for c in model.__table__.columns}
        )

    def _to_model(self, entity: T_Entity) -> T_Model:
        return self.model(**{k: v for k, v in entity.__dict__.items() if v is not None})

    async def create(self, entity: T_Entity) -> T_Entity:
        model = self._to_model(entity)
        # Si el ID es None (generación en BD) hay que removerlo o setear None al modelo real si venia un placeholder
        pk_name = self.model.__mapper__.primary_key[0].name
        if getattr(entity, pk_name, None) is None:
            setattr(model, pk_name, None)

        created_model = await super().create(model)
        return self._to_entity(created_model)

    async def get_by_id(self, id: UUID) -> T_Entity | None:
        model = await super().get_by_id(id)
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[T_Entity]:
        models = await super().get_all()
        return [self._to_entity(m) for m in models]

    async def update(self, entity: T_Entity) -> T_Entity:
        model = self._to_model(entity)
        merged_model = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged_model)
        return self._to_entity(merged_model)

    async def get_by_name(self, name: str) -> T_Entity | None:
        # Busca dinámicamente la columna 'name_' algo, asumiendo estructura
        name_col = next(
            (c for c in self.model.__table__.columns if "name" in c.name), None
        )
        if name_col is None:
            return None
        query = select(self.model).where(name_col == name)
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None


class SupplierRepository(
    SQLAlchemyCatalogRepository[SupplierModel, Supplier], ISupplierRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(SupplierModel, Supplier, session)


class ColorRepository(SQLAlchemyCatalogRepository[ColorModel, Color], IColorRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(ColorModel, Color, session)


class SizeRepository(SQLAlchemyCatalogRepository[SizeModel, Size], ISizeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(SizeModel, Size, session)


class CategoryRepository(
    SQLAlchemyCatalogRepository[CategoryModel, Category], ICategoryRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(CategoryModel, Category, session)


class GenderRepository(
    SQLAlchemyCatalogRepository[GenderModel, Gender], IGenderRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(GenderModel, Gender, session)
