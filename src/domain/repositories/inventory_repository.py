# Paso 9: src/domain/repositories/inventory_repository.py
"""
Interfaz de repositorio para la entidad Inventory y InventoryPhoto.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.inventory import Inventory, InventoryPhoto


class InventoryRepository(ABC):
    @abstractmethod
    async def create(self, inventory: Inventory) -> Inventory:
        pass

    @abstractmethod
    async def get_by_id(self, id_inventory: UUID) -> Inventory | None:
        pass

    @abstractmethod
    async def get_by_id_for_update(self, id_inventory: UUID) -> Inventory | None:
        """Obtiene y bloquea artículo hasta finalizar transacción actual."""
        pass

    @abstractmethod
    async def get_all(
        self,
        category_id: UUID | None = None,
        gender_id: UUID | None = None,
        color_id: UUID | None = None,
        size_id: UUID | None = None,
        is_active: bool | None = None,
        code_inventory: str | None = None,
        barcode_inventory: str | None = None,
        search: str | None = None,
    ) -> list[Inventory]:
        pass

    @abstractmethod
    async def update(self, inventory: Inventory) -> Inventory:
        pass


class InventoryPhotoRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id_reg: UUID) -> InventoryPhoto | None:
        pass

    @abstractmethod
    async def create(self, photo: InventoryPhoto) -> InventoryPhoto:
        pass

    @abstractmethod
    async def delete(self, id_reg: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_inventory_id(self, id_inventory: UUID) -> list[InventoryPhoto]:
        pass
