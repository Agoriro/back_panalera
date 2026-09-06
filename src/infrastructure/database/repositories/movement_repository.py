# Paso 12: src/infrastructure/database/repositories/movement_repository.py
"""
Implementación del repositorio de Movement.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.movement import Movement, MovementType
from src.domain.repositories.movement_repository import (
    MovementRepository as IMovementRepository,
)
from src.infrastructure.database.models.movement import MovementModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class MovementRepository(BaseRepository[MovementModel], IMovementRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(MovementModel, session)

    def _to_entity(self, model: MovementModel) -> Movement:
        movement_date = model.date
        if movement_date.tzinfo is None:
            movement_date = movement_date.replace(tzinfo=UTC)
        else:
            movement_date = movement_date.astimezone(UTC)
        return Movement(
            id_movement=model.id_movement,
            type_movement=model.type_movement,
            date=movement_date,
            id_supplier=model.id_supplier,
            id_inventory=model.id_inventory,
            quantity=model.quantity,
            value=model.value,
            unit_cost=model.unit_cost,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Movement) -> MovementModel:
        return MovementModel(
            id_movement=entity.id_movement,
            type_movement=entity.type_movement,
            date=entity.date,
            id_supplier=entity.id_supplier,
            id_inventory=entity.id_inventory,
            quantity=entity.quantity,
            value=entity.value,
            unit_cost=entity.unit_cost,
        )

    async def find_by_id(self, id: UUID, for_update: bool = False) -> Movement | None:
        query = select(MovementModel).where(MovementModel.id_movement == id)
        if for_update:
            query = query.with_for_update().execution_options(populate_existing=True)
        model = (await self.session.execute(query)).scalars().first()
        return self._to_entity(model) if model else None

    async def update_movement(self, movement: Movement) -> Movement:
        model = await super().get_by_id(movement.id_movement)
        if model is None:
            raise ValueError("Movimiento no encontrado")
        model.quantity = movement.quantity
        model.value = movement.value
        model.unit_cost = movement.unit_cost
        model.id_supplier = movement.id_supplier
        model.updated_at = datetime.now(UTC)
        updated = await super().update(model)
        return self._to_entity(updated)

    async def create(self, movement: Movement) -> Movement:
        model = self._to_model(movement)
        if not movement.id_movement:
            model.id_movement = None
        created_model = await super().create(model)
        return self._to_entity(created_model)

    async def get_all(
        self,
        type_movement: MovementType | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        id_inventory: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Movement], int]:
        filters = []

        if type_movement:
            filters.append(MovementModel.type_movement == type_movement)
        if date_from:
            filters.append(MovementModel.date >= date_from)
        if date_to:
            filters.append(MovementModel.date < date_to)
        if id_inventory:
            filters.append(MovementModel.id_inventory == id_inventory)

        total = await self.session.scalar(
            select(func.count()).select_from(MovementModel).where(*filters)
        )
        query = (
            select(MovementModel)
            .where(*filters)
            .order_by(desc(MovementModel.date), desc(MovementModel.id_movement))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()], int(total or 0)

    async def get_last_purchase_by_inventory(
        self, id_inventory: UUID
    ) -> Movement | None:
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

    async def get_stock(self, id_inventory: UUID) -> int:
        signed_quantity = case(
            (MovementModel.type_movement == MovementType.BUY, MovementModel.quantity),
            else_=-MovementModel.quantity,
        )
        query = select(func.coalesce(func.sum(signed_quantity), 0)).where(
            MovementModel.id_inventory == id_inventory
        )
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def get_sales_report(
        self,
        date_from: datetime | None,
        date_to: datetime | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Movement], int, Decimal, Decimal]:
        filters = [MovementModel.type_movement == MovementType.SELL]
        if date_from:
            filters.append(MovementModel.date >= date_from)
        if date_to:
            filters.append(MovementModel.date < date_to)
        totals_query = select(
            func.count(),
            func.coalesce(func.sum(MovementModel.value * MovementModel.quantity), 0),
            func.coalesce(
                func.sum(
                    (MovementModel.value - MovementModel.unit_cost)
                    * MovementModel.quantity
                ),
                0,
            ),
        ).where(*filters)
        total, revenue, profit = (await self.session.execute(totals_query)).one()
        query = (
            select(MovementModel)
            .where(*filters)
            .order_by(desc(MovementModel.date), desc(MovementModel.id_movement))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        sales = [self._to_entity(model) for model in result.scalars().all()]
        return sales, int(total), Decimal(revenue), Decimal(profit)

    async def get_inventory_report(self) -> list[tuple[UUID, int, int, int]]:
        from src.infrastructure.database.models.inventory import InventoryModel

        bought = func.coalesce(
            func.sum(
                case(
                    (
                        MovementModel.type_movement == MovementType.BUY,
                        MovementModel.quantity,
                    ),
                    else_=0,
                )
            ),
            0,
        )
        sold = func.coalesce(
            func.sum(
                case(
                    (
                        MovementModel.type_movement == MovementType.SELL,
                        MovementModel.quantity,
                    ),
                    else_=0,
                )
            ),
            0,
        )
        query = (
            select(InventoryModel.id_inventory, bought, sold, bought - sold)
            .outerjoin(
                MovementModel, MovementModel.id_inventory == InventoryModel.id_inventory
            )
            .group_by(InventoryModel.id_inventory)
            .order_by(InventoryModel.id_inventory)
        )
        rows = (await self.session.execute(query)).all()
        return [(row[0], int(row[1]), int(row[2]), int(row[3])) for row in rows]

    async def get_projection_report(
        self, date_from: datetime
    ) -> list[tuple[UUID, int]]:
        query = (
            select(MovementModel.id_inventory, func.sum(MovementModel.quantity))
            .where(MovementModel.type_movement == MovementType.SELL)
            .where(MovementModel.date >= date_from)
            .group_by(MovementModel.id_inventory)
            .order_by(MovementModel.id_inventory)
        )
        rows = (await self.session.execute(query)).all()
        return [(row[0], int(row[1])) for row in rows]
