# Paso 9: src/domain/repositories/catalog_repository.py
"""
Interfaces de repositorio para entidades del catálogo.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from src.domain.entities.catalog import Category, Color, Gender, Size, Supplier

T = TypeVar("T")


class BaseCatalogRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[T]:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> T | None:
        pass


class SupplierRepository(BaseCatalogRepository[Supplier]):
    pass


class ColorRepository(BaseCatalogRepository[Color]):
    pass


class SizeRepository(BaseCatalogRepository[Size]):
    pass


class CategoryRepository(BaseCatalogRepository[Category]):
    pass


class GenderRepository(BaseCatalogRepository[Gender]):
    pass
