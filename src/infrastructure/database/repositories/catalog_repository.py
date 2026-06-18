# Paso 12: src/infrastructure/database/repositories/catalog_repository.py
"""
Implementación de repositorios de catálogo.
"""
from typing import List, Optional, Type, TypeVar
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.catalog import Supplier, Color, Size, Category, Gender
from src.domain.repositories.catalog_repository import (
    SupplierRepository as ISupplierRepository,
    ColorRepository as IColorRepository,
    SizeRepository as ISizeRepository,
    CategoryRepository as ICategoryRepository,
    GenderRepository as IGenderRepository,
    BaseCatalogRepository
)
from src.infrastructure.database.models.catalog import (
    SupplierModel, ColorModel, SizeModel, CategoryModel, GenderModel
)
from src.infrastructure.database.repositories.base_repository import BaseRepository

T_Entity = TypeVar('T_Entity')
T_Model = TypeVar('T_Model')

class SQLAlchemyCatalogRepository(BaseRepository[T_Model], BaseCatalogRepository[T_Entity]):
    def __init__(self, model_cls: Type[T_Model], entity_cls: Type[T_Entity], session: AsyncSession):
        super().__init__(model_cls, session)
        self.entity_cls = entity_cls

    def _to_entity(self, model: T_Model) -> T_Entity:
        # Crea entidad dinámicamente mapeando los atributos
        return self.entity_cls(**{c.name: getattr(model, c.name) for c in model.__table__.columns})

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

    async def get_by_id(self, id: UUID) -> Optional[T_Entity]:
        model = await super().get_by_id(id)
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[T_Entity]:
        models = await super().get_all()
        return [self._to_entity(m) for m in models]

    async def update(self, entity: T_Entity) -> T_Entity:
        model = self._to_model(entity)
        merged_model = await self.session.merge(model)
        await self.session.commit()
        await self.session.refresh(merged_model)
        return self._to_entity(merged_model)

    async def get_by_name(self, name: str) -> Optional[T_Entity]:
        # Busca dinámicamente la columna 'name_' algo, asumiendo estructura
        name_col = next((c for c in self.model.__table__.columns if "name" in c.name), None)
        if name_col is None:
            return None
        query = select(self.model).where(name_col == name)
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

class SupplierRepository(SQLAlchemyCatalogRepository[Supplier, SupplierModel], ISupplierRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(SupplierModel, Supplier, session)

class ColorRepository(SQLAlchemyCatalogRepository[Color, ColorModel], IColorRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(ColorModel, Color, session)

class SizeRepository(SQLAlchemyCatalogRepository[Size, SizeModel], ISizeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(SizeModel, Size, session)

class CategoryRepository(SQLAlchemyCatalogRepository[Category, CategoryModel], ICategoryRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(CategoryModel, Category, session)

class GenderRepository(SQLAlchemyCatalogRepository[Gender, GenderModel], IGenderRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(GenderModel, Gender, session)
