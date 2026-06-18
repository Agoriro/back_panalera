# Paso 14: src/application/dtos/report_dto.py
from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class SaleReportItem(BaseModel):
    id_movement: UUID
    date: datetime
    id_inventory: UUID
    quantity: int
    value_sell: Decimal
    last_purchase_price: Decimal
    profit: Decimal

    model_config = ConfigDict(from_attributes=True)

class SalesReportResponse(BaseModel):
    items: List[SaleReportItem]
    total_revenue: Decimal
    total_profit: Decimal

class InventoryReportItem(BaseModel):
    id_inventory: UUID
    total_bought: int
    total_sold: int
    current_stock: int

class ProjectionReportItem(BaseModel):
    id_inventory: UUID
    average_monthly_sales: Decimal
    projected_sales_next_month: int
