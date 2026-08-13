# Paso 9: src/domain/repositories/inventory_repository.py
"""
Interfaz de repositorio para la entidad Inventory y InventoryPhoto.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.entities.inventory import Inventory, InventoryPhoto

class InventoryRepository(ABC):
    @abstractmethod
    async def create(self, inventory: Inventory) -> Inventory:
        pass

    @abstractmethod
    async def get_by_id(self, id_inventory: UUID) -> Optional[Inventory]:
        pass

    @abstractmethod
    async def get_all(self, category_id: Optional[UUID] = None, gender_id: Optional[UUID] = None, 
                      color_id: Optional[UUID] = None, size_id: Optional[UUID] = None, 
                      is_active: Optional[bool] = None, code_inventory: Optional[str] = None,
                      barcode_inventory: Optional[str] = None, search: Optional[str] = None) -> List[Inventory]:
        pass

    @abstractmethod
    async def update(self, inventory: Inventory) -> Inventory:
        pass

class InventoryPhotoRepository(ABC):
    @abstractmethod
    async def create(self, photo: InventoryPhoto) -> InventoryPhoto:
        pass

    @abstractmethod
    async def delete(self, id_reg: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_inventory_id(self, id_inventory: UUID) -> List[InventoryPhoto]:
        pass
