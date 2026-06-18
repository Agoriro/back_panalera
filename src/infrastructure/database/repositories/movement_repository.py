# Paso 12: src/infrastructure/database/repositories/movement_repository.py
"""
Implementación del repositorio de Movement.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.movement import Movement, MovementType
from src.domain.repositories.movement_repository import MovementRepository as IMovementRepository
from src.infrastructure.database.models.movement import MovementModel
from src.infrastructure.database.repositories.base_repository import BaseRepository

class MovementRepository(BaseRepository[MovementModel], IMovementRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(MovementModel, session)

    def _to_entity(self, model: MovementModel) -> Movement:
        return Movement(
            id_movement=model.id_movement,
            type_movement=model.type_movement,
            date=model.date,
            id_supplier=model.id_supplier,
            id_inventory=model.id_inventory,
            quantity=model.quantity,
            value=model.value,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: Movement) -> MovementModel:
        return MovementModel(
            id_movement=entity.id_movement,
            type_movement=entity.type_movement,
            date=entity.date,
            id_supplier=entity.id_supplier,
            id_inventory=entity.id_inventory,
            quantity=entity.quantity,
            value=entity.value
        )

    async def create(self, movement: Movement) -> Movement:
        model = self._to_model(movement)
        if not movement.id_movement:
            model.id_movement = None
        created_model = await super().create(model)
        return self._to_entity(created_model)

    async def get_all(self, type_movement: Optional[MovementType] = None, 
                      date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                      id_inventory: Optional[UUID] = None) -> List[Movement]:
        query = select(MovementModel)
        
        if type_movement:
            query = query.where(MovementModel.type_movement == type_movement)
        if date_from:
            query = query.where(MovementModel.date >= date_from)
        if date_to:
            query = query.where(MovementModel.date <= date_to)
        if id_inventory:
            query = query.where(MovementModel.id_inventory == id_inventory)
            
        query = query.order_by(desc(MovementModel.date))
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_last_purchase_by_inventory(self, id_inventory: UUID) -> Optional[Movement]:
        query = (
            select(MovementModel)
            .where(MovementModel.id_inventory == id_inventory)
            .where(MovementModel.type_movement == MovementType.BUY)
            .order_by(desc(MovementModel.date))
            .limit(1)
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        return self._to_entity(model) if model else None
