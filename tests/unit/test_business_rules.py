# Paso 19: tests/unit/test_business_rules.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from uuid import uuid4

from src.application.use_cases.movement_use_case import MovementUseCase
from src.application.use_cases.report_use_case import ReportUseCase
from src.application.dtos.movement_dto import SaleCreate
from src.domain.entities.movement import MovementType, Movement
from src.domain.entities.inventory import Inventory
from src.shared.exceptions.domain_exceptions import BusinessRuleValidationException

@pytest.mark.asyncio
async def test_calculate_sell_price():
    # Arrange
    movement_repo = AsyncMock()
    inv_repo = AsyncMock()
    supplier_repo = AsyncMock()

    use_case = MovementUseCase(movement_repo, inv_repo, supplier_repo)
    
    id_inv = uuid4()
    
    inv_repo.get_by_id.return_value = Inventory(
        id_inventory=id_inv, description_inventory="Test", utility=Decimal('0.35'),
        id_supplier=uuid4(), id_color=uuid4(), id_size=uuid4(), id_category=uuid4(), id_gender=uuid4(), is_active=True
    )
    
    movement_repo.get_last_purchase_by_inventory.return_value = Movement(
        id_movement=uuid4(), type_movement=MovementType.BUY, date=None, id_supplier=uuid4(),
        id_inventory=id_inv, quantity=10, value=Decimal('100.00')
    )
    
    movement_repo.create.return_value = MagicMock()
    
    sale_data = SaleCreate(id_inventory=id_inv, quantity=2)

    # Act
    await use_case.register_sale(sale_data)

    # Assert
    # Verificar que create fue llamado con value = 100 * (1 + 0.35) = 135.00
    created_movement = movement_repo.create.call_args[0][0]
    assert created_movement.type_movement == MovementType.SELL
    assert created_movement.value == Decimal('135.00')

@pytest.mark.asyncio
async def test_calculate_sell_price_without_purchase_fails():
    movement_repo = AsyncMock()
    inv_repo = AsyncMock()
    supplier_repo = AsyncMock()

    use_case = MovementUseCase(movement_repo, inv_repo, supplier_repo)
    id_inv = uuid4()
    
    inv_repo.get_by_id.return_value = Inventory(
        id_inventory=id_inv, description_inventory="Test", utility=Decimal('0.35'),
        id_supplier=uuid4(), id_color=uuid4(), id_size=uuid4(), id_category=uuid4(), id_gender=uuid4(), is_active=True
    )
    
    movement_repo.get_last_purchase_by_inventory.return_value = None
    
    sale_data = SaleCreate(id_inventory=id_inv, quantity=2)

    with pytest.raises(BusinessRuleValidationException):
        await use_case.register_sale(sale_data)

@pytest.mark.asyncio
async def test_calculate_inventory_report():
    movement_repo = AsyncMock()
    inv_repo = AsyncMock()
    
    use_case = ReportUseCase(movement_repo, inv_repo)
    id_inv = uuid4()
    
    movement_repo.get_all.return_value = [
        Movement(id_movement=uuid4(), type_movement=MovementType.BUY, date=None, id_supplier=None, id_inventory=id_inv, quantity=10, value=Decimal('10')),
        Movement(id_movement=uuid4(), type_movement=MovementType.SELL, date=None, id_supplier=None, id_inventory=id_inv, quantity=3, value=Decimal('15')),
        Movement(id_movement=uuid4(), type_movement=MovementType.SELL, date=None, id_supplier=None, id_inventory=id_inv, quantity=2, value=Decimal('15'))
    ]
    
    report = await use_case.get_inventory_report()
    
    assert len(report) == 1
    assert report[0].id_inventory == id_inv
    assert report[0].total_bought == 10
    assert report[0].total_sold == 5
    assert report[0].current_stock == 5
