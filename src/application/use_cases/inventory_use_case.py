# Paso 15: src/application/use_cases/inventory_use_case.py
from typing import List, Optional
from uuid import UUID
from src.application.dtos.inventory_dto import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryPhotoCreate, InventoryPhotoResponse
from src.domain.entities.inventory import Inventory, InventoryPhoto
from src.domain.repositories.inventory_repository import InventoryRepository, InventoryPhotoRepository
from src.domain.repositories.catalog_repository import SupplierRepository, ColorRepository, SizeRepository, CategoryRepository, GenderRepository
from src.shared.exceptions.domain_exceptions import ResourceNotFoundException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

class InventoryUseCase:
    def __init__(self, inv_repo: InventoryRepository, photo_repo: InventoryPhotoRepository,
                 supplier_repo: SupplierRepository, color_repo: ColorRepository,
                 size_repo: SizeRepository, category_repo: CategoryRepository,
                 gender_repo: GenderRepository):
        self.inv_repo = inv_repo
        self.photo_repo = photo_repo
        self.supplier_repo = supplier_repo
        self.color_repo = color_repo
        self.size_repo = size_repo
        self.category_repo = category_repo
        self.gender_repo = gender_repo

    async def _validate_relations(self, data):
        if not await self.supplier_repo.get_by_id(data.id_supplier): raise ResourceNotFoundException("Supplier no encontrado")
        if not await self.color_repo.get_by_id(data.id_color): raise ResourceNotFoundException("Color no encontrado")
        if not await self.size_repo.get_by_id(data.id_size): raise ResourceNotFoundException("Size no encontrado")
        if not await self.category_repo.get_by_id(data.id_category): raise ResourceNotFoundException("Category no encontrado")
        if not await self.gender_repo.get_by_id(data.id_gender): raise ResourceNotFoundException("Gender no encontrado")

    async def create(self, data: InventoryCreate) -> InventoryResponse:
        logger.info("Creando artículo en inventario", desc=data.description_inventory)
        await self._validate_relations(data)
        
        inventory = Inventory(
            id_inventory=None, # type: ignore
            description_inventory=data.description_inventory,
            code_inventory=data.code_inventory,
            barcode_inventory=data.barcode_inventory,
            utility=data.utility,
            id_supplier=data.id_supplier,
            id_color=data.id_color,
            id_size=data.id_size,
            id_category=data.id_category,
            id_gender=data.id_gender,
            is_active=True
        )
        created_inv = await self.inv_repo.create(inventory)
        return InventoryResponse.model_validate(created_inv)

    async def get_all(self, category_id: Optional[UUID] = None, gender_id: Optional[UUID] = None, 
                      color_id: Optional[UUID] = None, size_id: Optional[UUID] = None, 
                      is_active: Optional[bool] = None, code_inventory: Optional[str] = None,
                      barcode_inventory: Optional[str] = None, search: Optional[str] = None) -> List[InventoryResponse]:
        inventories = await self.inv_repo.get_all(category_id, gender_id, color_id, size_id, is_active, code_inventory, barcode_inventory, search)
        return [InventoryResponse.model_validate(i) for i in inventories]

    async def get_by_id(self, id_inventory: UUID) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")
        return InventoryResponse.model_validate(inventory)

    async def update(self, id_inventory: UUID, data: InventoryUpdate) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")
            
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(inventory, key, value)
            
        # Re-validar si se actualizaron las llaves foraneas (simplificado, se puede optimizar)
        # asumiendo que el request envia datos válidos o falla la FK en DB (por Clean Arch es mejor validar antes)
        
        updated_inv = await self.inv_repo.update(inventory)
        return InventoryResponse.model_validate(updated_inv)

    async def toggle_active(self, id_inventory: UUID) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")
        inventory.is_active = not inventory.is_active
        updated_inv = await self.inv_repo.update(inventory)
        return InventoryResponse.model_validate(updated_inv)

    async def add_photos(self, id_inventory: UUID, data: InventoryPhotoCreate) -> List[InventoryPhotoResponse]:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")
            
        photos = []
        for url in data.url_photos:
            photo = InventoryPhoto(id_reg=None, id_inventory=id_inventory, url_photo=url) # type: ignore
            created_photo = await self.photo_repo.create(photo)
            photos.append(InventoryPhotoResponse.model_validate(created_photo))
        return photos

    async def delete_photo(self, id_inventory: UUID, id_photo: UUID) -> None:
        deleted = await self.photo_repo.delete(id_photo)
        if not deleted:
            raise ResourceNotFoundException("Foto no encontrada")
