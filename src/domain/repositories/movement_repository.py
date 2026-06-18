# Paso 9: src/domain/repositories/movement_repository.py
"""
Interfaz de repositorio para la entidad Movement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.movement import Movement, MovementType

class MovementRepository(ABC):
    @abstractmethod
    async def create(self, movement: Movement) -> Movement:
        pass

    @abstractmethod
    async def get_all(self, type_movement: Optional[MovementType] = None, 
                      date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                      id_inventory: Optional[UUID] = None) -> List[Movement]:
        pass

    @abstractmethod
    async def get_last_purchase_by_inventory(self, id_inventory: UUID) -> Optional[Movement]:
        """Obtiene la compra más reciente para un artículo específico, necesario para calcular el precio de venta."""
        pass
