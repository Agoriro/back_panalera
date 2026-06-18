# Paso 9: src/domain/repositories/catalog_repository.py
"""
Interfaces de repositorio para entidades del catálogo.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from uuid import UUID
from src.domain.entities.catalog import Supplier, Color, Size, Category, Gender

T = TypeVar('T')

class BaseCatalogRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[T]:
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
