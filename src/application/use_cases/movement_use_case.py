# Paso 15: src/application/use_cases/movement_use_case.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.application.dtos.movement_dto import PurchaseCreate, SaleCreate, MovementResponse
from src.domain.entities.movement import Movement, MovementType
from src.domain.repositories.movement_repository import MovementRepository
from src.domain.repositories.inventory_repository import InventoryRepository
from src.domain.repositories.catalog_repository import SupplierRepository
from src.shared.exceptions.domain_exceptions import ResourceNotFoundException, BusinessRuleValidationException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

class MovementUseCase:
    def __init__(self, movement_repo: MovementRepository, inv_repo: InventoryRepository, supplier_repo: SupplierRepository):
        self.movement_repo = movement_repo
        self.inv_repo = inv_repo
        self.supplier_repo = supplier_repo

    async def register_purchase(self, data: PurchaseCreate) -> MovementResponse:
        logger.info("Registrando compra", id_inventory=str(data.id_inventory), qty=data.quantity)
        
        inventory = await self.inv_repo.get_by_id(data.id_inventory)
        if not inventory or not inventory.is_active:
            raise ResourceNotFoundException("Artículo de inventario no encontrado o inactivo")
            
        supplier = await self.supplier_repo.get_by_id(data.id_supplier)
        if not supplier or not supplier.is_active:
            raise ResourceNotFoundException("Proveedor no encontrado o inactivo")

        movement = Movement(
            id_movement=None, # type: ignore
            type_movement=MovementType.BUY,
            date=datetime.now(),
            id_supplier=data.id_supplier,
            id_inventory=data.id_inventory,
            quantity=data.quantity,
            value=data.value
        )
        
        created_mov = await self.movement_repo.create(movement)
        return MovementResponse.model_validate(created_mov)

    async def register_sale(self, data: SaleCreate) -> MovementResponse:
        logger.info("Registrando venta", id_inventory=str(data.id_inventory), qty=data.quantity)
        
        inventory = await self.inv_repo.get_by_id(data.id_inventory)
        if not inventory or not inventory.is_active:
            raise ResourceNotFoundException("Artículo de inventario no encontrado o inactivo")

        # REGLA DE NEGOCIO: value = último_precio_de_compra * (1 + utility)
        last_purchase = await self.movement_repo.get_last_purchase_by_inventory(data.id_inventory)
        if not last_purchase:
            raise BusinessRuleValidationException("No se puede vender un artículo que no tiene compras registradas")

        # Utility viene como porcentaje (ej 0.35 para 35%)
        sell_value = last_purchase.value * (1 + inventory.utility)

        # Opcional: Validar existencias antes de vender
        # (se pide en el reporte, pero es buena práctica no dejar vender si qty > stock)
        
        movement = Movement(
            id_movement=None, # type: ignore
            type_movement=MovementType.SELL,
            date=datetime.now(),
            id_supplier=None,
            id_inventory=data.id_inventory,
            quantity=data.quantity,
            value=sell_value
        )
        
        created_mov = await self.movement_repo.create(movement)
        return MovementResponse.model_validate(created_mov)

    async def get_all(self, type_movement: Optional[MovementType] = None, 
                      date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                      id_inventory: Optional[UUID] = None) -> List[MovementResponse]:
        movements = await self.movement_repo.get_all(type_movement, date_from, date_to, id_inventory)
        return [MovementResponse.model_validate(m) for m in movements]
