# Paso 15: src/application/use_cases/inventory_use_case.py
from uuid import UUID

from src.application.dtos.inventory_dto import (
    MAX_INVENTORY_PHOTOS,
    InventoryCreate,
    InventoryPhotoCreate,
    InventoryPhotoResponse,
    InventoryResponse,
    InventoryUpdate,
)
from src.application.dtos.pagination_dto import Page, build_page
from src.domain.entities.inventory import Inventory, InventoryPhoto
from src.domain.repositories.catalog_repository import (
    CategoryRepository,
    ColorRepository,
    GenderRepository,
    SizeRepository,
    SupplierRepository,
)
from src.domain.repositories.inventory_repository import (
    InventoryPhotoRepository,
    InventoryRepository,
)
from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    ResourceNotFoundException,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class InventoryUseCase:
    def __init__(
        self,
        inv_repo: InventoryRepository,
        photo_repo: InventoryPhotoRepository,
        supplier_repo: SupplierRepository,
        color_repo: ColorRepository,
        size_repo: SizeRepository,
        category_repo: CategoryRepository,
        gender_repo: GenderRepository,
    ):
        self.inv_repo = inv_repo
        self.photo_repo = photo_repo
        self.supplier_repo = supplier_repo
        self.color_repo = color_repo
        self.size_repo = size_repo
        self.category_repo = category_repo
        self.gender_repo = gender_repo

    async def _validate_relations(self, data) -> None:
        relations = (
            ("id_supplier", self.supplier_repo, "Supplier"),
            ("id_color", self.color_repo, "Color"),
            ("id_size", self.size_repo, "Size"),
            ("id_category", self.category_repo, "Category"),
            ("id_gender", self.gender_repo, "Gender"),
        )
        for field, repository, label in relations:
            if field in data.model_fields_set and not await repository.get_by_id(
                getattr(data, field)
            ):
                raise ResourceNotFoundException(f"{label} no encontrado")

    async def create(self, data: InventoryCreate) -> InventoryResponse:
        logger.info("Creando artículo en inventario", desc=data.description_inventory)
        await self._validate_relations(data)

        inventory = Inventory(
            id_inventory=None,
            description_inventory=data.description_inventory,
            code_inventory=data.code_inventory,
            barcode_inventory=data.barcode_inventory,
            utility=data.utility,
            id_supplier=data.id_supplier,
            id_color=data.id_color,
            id_size=data.id_size,
            id_category=data.id_category,
            id_gender=data.id_gender,
            is_active=True,
        )
        created_inv = await self.inv_repo.create(inventory)
        return InventoryResponse.model_validate(created_inv)

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
        page: int = 1,
        page_size: int = 50,
    ) -> Page[InventoryResponse]:
        inventories, total = await self.inv_repo.get_all(
            category_id,
            gender_id,
            color_id,
            size_id,
            is_active,
            code_inventory,
            barcode_inventory,
            search,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        items = [InventoryResponse.model_validate(i) for i in inventories]
        return build_page(items, total, page, page_size)

    async def get_by_id(self, id_inventory: UUID) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")

        return InventoryResponse.model_validate(inventory)

    async def update(
        self, id_inventory: UUID, data: InventoryUpdate
    ) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")

        await self._validate_relations(data)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(inventory, key, value)

        updated_inv = await self.inv_repo.update(inventory)
        return InventoryResponse.model_validate(updated_inv)

    async def toggle_active(self, id_inventory: UUID) -> InventoryResponse:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")
        inventory.is_active = not inventory.is_active
        updated_inv = await self.inv_repo.update(inventory)
        return InventoryResponse.model_validate(updated_inv)

    async def add_photos(
        self, id_inventory: UUID, data: InventoryPhotoCreate
    ) -> list[InventoryPhotoResponse]:
        inventory = await self.inv_repo.get_by_id(id_inventory)
        if not inventory:
            raise ResourceNotFoundException("Artículo no encontrado")

        existing_photos = await self.photo_repo.get_by_inventory_id(id_inventory)
        if len(existing_photos) + len(data.url_photos) > MAX_INVENTORY_PHOTOS:
            raise BusinessRuleValidationException(
                f"Máximo {MAX_INVENTORY_PHOTOS} fotos por artículo"
            )

        photos = []
        for url in data.url_photos:
            photo = InventoryPhoto(
                id_reg=None, id_inventory=id_inventory, url_photo=str(url)
            )
            created_photo = await self.photo_repo.create(photo)
            photos.append(InventoryPhotoResponse.model_validate(created_photo))
        return photos

    async def delete_photo(self, id_inventory: UUID, id_photo: UUID) -> None:
        photo = await self.photo_repo.get_by_id(id_photo)
        if not photo or photo.id_inventory != id_inventory:
            raise ResourceNotFoundException("Foto no encontrada para este artículo")
        deleted = await self.photo_repo.delete(id_photo)
        if not deleted:
            raise ResourceNotFoundException("Foto no encontrada")
