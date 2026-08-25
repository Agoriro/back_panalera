# Paso 9: src/domain/repositories/movement_repository.py
"""
Interfaz de repositorio para la entidad Movement.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.movement import Movement, MovementType


class MovementRepository(ABC):
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
    ) -> list[Movement]:
        pass

    @abstractmethod
    async def get_last_purchase_by_inventory(
        self, id_inventory: UUID
    ) -> Movement | None:
        """Obtiene la compra más reciente para un artículo específico, necesario para calcular el precio de venta."""
        pass
