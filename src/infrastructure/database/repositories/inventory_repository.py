# Paso 12: src/infrastructure/database/repositories/inventory_repository.py
"""
Implementación de repositorios de inventario.
"""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.inventory import Inventory, InventoryPhoto
from src.domain.repositories.inventory_repository import (
    InventoryPhotoRepository as IInventoryPhotoRepository,
)
from src.domain.repositories.inventory_repository import (
    InventoryRepository as IInventoryRepository,
)
from src.infrastructure.database.errors import translate_integrity_error
from src.infrastructure.database.models.inventory import (
    InventoryModel,
    InventoryPhotoModel,
)
from src.infrastructure.database.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[InventoryModel], IInventoryRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(InventoryModel, session)

    def _to_entity(self, model: InventoryModel) -> Inventory:
        photos = [
            InventoryPhoto(
                id_reg=p.id_reg,
                id_inventory=p.id_inventory,
                url_photo=p.url_photo,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in getattr(model, "photos", [])
        ]

        return Inventory(
            id_inventory=model.id_inventory,
            description_inventory=model.description_inventory,
            utility=model.utility,
            id_supplier=model.id_supplier,
            id_color=model.id_color,
            id_size=model.id_size,
            id_category=model.id_category,
            id_gender=model.id_gender,
            is_active=model.is_active,
            code_inventory=model.code_inventory,
            barcode_inventory=model.barcode_inventory,
            created_at=model.created_at,
            updated_at=model.updated_at,
            photos=photos,
        )

    def _to_model(self, entity: Inventory) -> InventoryModel:
        return InventoryModel(
            id_inventory=entity.id_inventory,
            description_inventory=entity.description_inventory,
            utility=entity.utility,
            id_supplier=entity.id_supplier,
            id_color=entity.id_color,
            id_size=entity.id_size,
            id_category=entity.id_category,
            id_gender=entity.id_gender,
            is_active=entity.is_active,
            code_inventory=entity.code_inventory,
            barcode_inventory=entity.barcode_inventory,
        )

    async def create(self, inventory: Inventory) -> Inventory:
        model = self._to_model(inventory)
        if not inventory.id_inventory:
            model.id_inventory = None
        try:
            created_model = await super().create(model)
        except IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        return self._to_entity(created_model)

    async def get_by_id(self, id_inventory: UUID) -> Inventory | None:
        query = (
            select(InventoryModel)
            .options(selectinload(InventoryModel.photos))
            .where(InventoryModel.id_inventory == id_inventory)
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_id_for_update(self, id_inventory: UUID) -> Inventory | None:
        query = (
            select(InventoryModel)
            .options(selectinload(InventoryModel.photos))
            .where(InventoryModel.id_inventory == id_inventory)
            .with_for_update()
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

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
        query = select(InventoryModel).options(selectinload(InventoryModel.photos))
        if category_id:
            query = query.where(InventoryModel.id_category == category_id)
        if gender_id:
            query = query.where(InventoryModel.id_gender == gender_id)
        if color_id:
            query = query.where(InventoryModel.id_color == color_id)
        if size_id:
            query = query.where(InventoryModel.id_size == size_id)
        if is_active is not None:
            query = query.where(InventoryModel.is_active == is_active)
        if code_inventory:
            query = query.where(InventoryModel.code_inventory == code_inventory)
        if barcode_inventory:
            query = query.where(InventoryModel.barcode_inventory == barcode_inventory)

        if search and search.strip():
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                or_(
                    InventoryModel.description_inventory.ilike(search_pattern),
                    InventoryModel.code_inventory.ilike(search_pattern),
                    InventoryModel.barcode_inventory.ilike(search_pattern),
                )
            )

        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, inventory: Inventory) -> Inventory:
        model = self._to_model(inventory)
        merged_model = await self.session.merge(model)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        # Obtenemos de nuevo para cargar relaciones
        return await self.get_by_id(merged_model.id_inventory)


class InventoryPhotoRepository(
    BaseRepository[InventoryPhotoModel], IInventoryPhotoRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(InventoryPhotoModel, session)

    def _to_entity(self, model: InventoryPhotoModel) -> InventoryPhoto:
        return InventoryPhoto(
            id_reg=model.id_reg,
            id_inventory=model.id_inventory,
            url_photo=model.url_photo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, id_reg: UUID) -> InventoryPhoto | None:
        model = await super().get_by_id(id_reg)
        return self._to_entity(model) if model else None

    async def create(self, photo: InventoryPhoto) -> InventoryPhoto:
        model = InventoryPhotoModel(
            id_inventory=photo.id_inventory, url_photo=photo.url_photo
        )
        try:
            created_model = await super().create(model)
        except IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        return self._to_entity(created_model)

    async def delete(self, id_reg: UUID) -> bool:
        model = await super().get_by_id(id_reg)
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def get_by_inventory_id(self, id_inventory: UUID) -> list[InventoryPhoto]:
        query = select(InventoryPhotoModel).where(
            InventoryPhotoModel.id_inventory == id_inventory
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]
