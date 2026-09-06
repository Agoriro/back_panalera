# Paso 15: src/application/use_cases/movement_use_case.py
from datetime import UTC, datetime
from uuid import UUID

from src.application.date_ranges import normalize_date_range
from src.application.dtos.movement_dto import (
    MovementResponse,
    MovementUpdate,
    PurchaseCreate,
    SaleCreate,
)
from src.application.dtos.pagination_dto import Page, build_page
from src.domain.entities.movement import Movement, MovementType
from src.domain.repositories.catalog_repository import SupplierRepository
from src.domain.repositories.inventory_repository import InventoryRepository
from src.domain.repositories.movement_repository import MovementRepository
from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    ResourceNotFoundException,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class MovementUseCase:
    def __init__(
        self,
        movement_repo: MovementRepository,
        inv_repo: InventoryRepository,
        supplier_repo: SupplierRepository,
    ):
        self.movement_repo = movement_repo
        self.inv_repo = inv_repo
        self.supplier_repo = supplier_repo

    async def register_purchase(self, data: PurchaseCreate) -> MovementResponse:
        logger.info(
            "Registrando compra", id_inventory=str(data.id_inventory), qty=data.quantity
        )

        inventory = await self.inv_repo.get_by_id_for_update(data.id_inventory)
        if not inventory or not inventory.is_active:
            raise ResourceNotFoundException(
                "Artículo de inventario no encontrado o inactivo"
            )

        supplier = await self.supplier_repo.get_by_id(data.id_supplier)
        if not supplier or not supplier.is_active:
            raise ResourceNotFoundException("Proveedor no encontrado o inactivo")

        movement = Movement(
            id_movement=None,
            type_movement=MovementType.BUY,
            date=datetime.now(UTC),
            id_supplier=data.id_supplier,
            id_inventory=data.id_inventory,
            quantity=data.quantity,
            value=data.value,
            unit_cost=data.value,
        )

        created_mov = await self.movement_repo.create(movement)
        return MovementResponse.model_validate(created_mov)

    async def register_sale(self, data: SaleCreate) -> MovementResponse:
        logger.info(
            "Registrando venta", id_inventory=str(data.id_inventory), qty=data.quantity
        )

        inventory = await self.inv_repo.get_by_id_for_update(data.id_inventory)
        if not inventory or not inventory.is_active:
            raise ResourceNotFoundException(
                "Artículo de inventario no encontrado o inactivo"
            )

        # REGLA DE NEGOCIO: value = último_precio_de_compra * (1 + utility)
        last_purchase = await self.movement_repo.get_last_purchase_by_inventory(
            data.id_inventory
        )
        if not last_purchase:
            raise BusinessRuleValidationException(
                "No se puede vender un artículo que no tiene compras registradas"
            )

        current_stock = await self.movement_repo.get_stock(data.id_inventory)
        if data.quantity > current_stock:
            raise BusinessRuleValidationException(
                f"Stock insuficiente: disponible {current_stock}, solicitado {data.quantity}"
            )

        # Utility viene como porcentaje (ej 0.35 para 35%)
        sell_value = last_purchase.value * (1 + inventory.utility)

        movement = Movement(
            id_movement=None,
            type_movement=MovementType.SELL,
            date=datetime.now(UTC),
            id_supplier=None,
            id_inventory=data.id_inventory,
            quantity=data.quantity,
            value=sell_value,
            unit_cost=last_purchase.value,
        )

        created_mov = await self.movement_repo.create(movement)
        return MovementResponse.model_validate(created_mov)

    async def update(self, id: UUID, data: MovementUpdate) -> MovementResponse:
        movement = await self.movement_repo.find_by_id(id)
        if movement is None:
            raise ResourceNotFoundException("Movimiento no encontrado")

        # Same inventory lock as creation: serialize stock checks and writes.
        inventory = await self.inv_repo.get_by_id_for_update(movement.id_inventory)
        if inventory is None:
            raise ResourceNotFoundException("Artículo de inventario no encontrado")
        movement = await self.movement_repo.find_by_id(id, for_update=True)
        if movement is None:
            raise ResourceNotFoundException("Movimiento no encontrado")

        stock = await self.movement_repo.get_stock(movement.id_inventory)
        sign = 1 if movement.type_movement == MovementType.BUY else -1
        resulting_stock = stock + sign * (data.quantity - movement.quantity)
        if resulting_stock < 0:
            raise BusinessRuleValidationException(
                "La modificación dejaría existencias negativas. Revisa la cantidad."
            )

        if movement.type_movement == MovementType.BUY:
            supplier_id = data.id_supplier or movement.id_supplier
            if supplier_id != movement.id_supplier:
                supplier = await self.supplier_repo.get_by_id(supplier_id)
                if supplier is None or not supplier.is_active:
                    raise ResourceNotFoundException(
                        "Proveedor no encontrado o inactivo"
                    )
            movement.id_supplier = supplier_id
            movement.unit_cost = data.value
        else:
            if data.id_supplier is not None:
                raise BusinessRuleValidationException("Una venta no admite proveedor")
            # Preserve historical sale cost; later purchases must not reprice it.
            minimum_price = movement.unit_cost * (1 + inventory.utility)
            if data.value != movement.value and data.value < minimum_price:
                raise BusinessRuleValidationException(
                    f"El precio no puede ser inferior al sugerido ({minimum_price})."
                )

        movement.quantity = data.quantity
        movement.value = data.value
        updated = await self.movement_repo.update_movement(movement)
        return MovementResponse.model_validate(updated)

    async def get_all(
        self,
        type_movement: MovementType | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        id_inventory: UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Page[MovementResponse]:
        date_from, date_to = normalize_date_range(date_from, date_to)
        movements, total = await self.movement_repo.get_all(
            type_movement,
            date_from,
            date_to,
            id_inventory,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        items = [MovementResponse.model_validate(m) for m in movements]
        return build_page(items, total, page, page_size)
