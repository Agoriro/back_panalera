from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.application.dtos.movement_dto import MovementUpdate
from src.application.use_cases.movement_use_case import MovementUseCase
from src.domain.entities.movement import Movement, MovementType
from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    ResourceNotFoundException,
)


def setup_edit(kind, quantity=5, stock=3):
    movement = Movement(
        id_movement=uuid4(),
        type_movement=kind,
        date=datetime.now(UTC),
        id_supplier=uuid4() if kind == MovementType.BUY else None,
        id_inventory=uuid4(),
        quantity=quantity,
        value=Decimal("130"),
        unit_cost=Decimal("100"),
    )
    repo, inventory, suppliers = AsyncMock(), AsyncMock(), AsyncMock()
    repo.find_by_id.return_value = movement
    repo.get_stock.return_value = stock
    repo.update_movement.side_effect = lambda item: item
    inventory.get_by_id_for_update.return_value = SimpleNamespace(
        utility=Decimal("0.30")
    )
    suppliers.get_by_id.return_value = SimpleNamespace(is_active=True)
    return MovementUseCase(repo, inventory, suppliers), repo, movement


@pytest.mark.parametrize(
    "kind,quantity", [(MovementType.BUY, 1), (MovementType.SELL, 9)]
)
async def test_edit_rejects_negative_stock(kind, quantity):
    use_case, repo, movement = setup_edit(kind)
    with pytest.raises(BusinessRuleValidationException):
        await use_case.update(
            movement.id_movement, MovementUpdate(quantity=quantity, value=130)
        )
    repo.update_movement.assert_not_awaited()


async def test_sale_edit_counts_original_quantity_and_preserves_history():
    use_case, repo, movement = setup_edit(MovementType.SELL, stock=0)
    original_date, original_id = movement.date, movement.id_movement
    result = await use_case.update(original_id, MovementUpdate(quantity=4, value=140))
    assert result.quantity == 4
    assert result.unit_cost == Decimal("100")
    assert result.date == original_date
    assert result.id_movement == original_id
    repo.find_by_id.assert_awaited_with(original_id, for_update=True)
    repo.create.assert_not_awaited()


async def test_purchase_edit_updates_supplier_and_cost():
    use_case, repo, movement = setup_edit(MovementType.BUY)
    supplier = uuid4()
    result = await use_case.update(
        movement.id_movement, MovementUpdate(quantity=2, value=90, id_supplier=supplier)
    )
    assert result.quantity == 2
    assert result.value == result.unit_cost == Decimal("90")
    assert result.id_supplier == supplier
    repo.update_movement.assert_awaited_once()


async def test_missing_movement():
    use_case, repo, _ = setup_edit(MovementType.BUY)
    repo.find_by_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        await use_case.update(uuid4(), MovementUpdate(quantity=1, value=100))


async def test_inactive_new_supplier():
    use_case, repo, movement = setup_edit(MovementType.BUY)
    use_case.supplier_repo.get_by_id.return_value = SimpleNamespace(is_active=False)
    with pytest.raises(ResourceNotFoundException):
        await use_case.update(
            movement.id_movement,
            MovementUpdate(quantity=5, value=100, id_supplier=uuid4()),
        )
    repo.update_movement.assert_not_awaited()


async def test_sale_rejects_price_below_historical_cost_with_utility():
    use_case, repo, movement = setup_edit(MovementType.SELL)
    with pytest.raises(BusinessRuleValidationException):
        await use_case.update(
            movement.id_movement, MovementUpdate(quantity=5, value=120)
        )
    repo.update_movement.assert_not_awaited()


async def test_sale_rejects_supplier():
    use_case, repo, movement = setup_edit(MovementType.SELL)
    with pytest.raises(BusinessRuleValidationException):
        await use_case.update(
            movement.id_movement,
            MovementUpdate(quantity=5, value=130, id_supplier=uuid4()),
        )
    repo.update_movement.assert_not_awaited()


@pytest.mark.parametrize(
    "data",
    [
        {"quantity": 0, "value": 1},
        {"quantity": 1, "value": 0},
        {"quantity": 1.5, "value": 1},
        {"quantity": 1, "value": 1, "id_inventory": str(uuid4())},
    ],
)
def test_invalid_edit_payload(data):
    with pytest.raises(ValidationError):
        MovementUpdate(**data)
