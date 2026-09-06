# Paso 9: src/domain/repositories/movement_repository.py
"""
Interfaz de repositorio para la entidad Movement.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.movement import Movement, MovementType


class MovementRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: UUID, for_update: bool = False) -> Movement | None:
        pass

    @abstractmethod
    async def update_movement(self, movement: Movement) -> Movement:
        pass

    @abstractmethod
    async def create(self, movement: Movement) -> Movement:
        pass

    @abstractmethod
    async def get_all(
        self,
        type_movement: MovementType | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        id_inventory: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Movement], int]:
        pass

    @abstractmethod
    async def get_last_purchase_by_inventory(
        self, id_inventory: UUID
    ) -> Movement | None:
        """Obtiene la compra más reciente para un artículo específico, necesario para calcular el precio de venta."""
        pass

    @abstractmethod
    async def get_stock(self, id_inventory: UUID) -> int:
        """Calcula compras menos ventas dentro de transacción actual."""
        pass

    @abstractmethod
    async def get_sales_report(
        self,
        date_from: datetime | None,
        date_to: datetime | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Movement], int, Decimal, Decimal]:
        pass

    @abstractmethod
    async def get_inventory_report(self) -> list[tuple[UUID, int, int, int]]:
        pass

    @abstractmethod
    async def get_projection_report(
        self, date_from: datetime
    ) -> list[tuple[UUID, int]]:
        pass
