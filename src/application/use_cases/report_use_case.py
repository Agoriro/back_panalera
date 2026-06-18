# Paso 15: src/application/use_cases/report_use_case.py
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from collections import defaultdict
from decimal import Decimal

from src.application.dtos.report_dto import SalesReportResponse, SaleReportItem, InventoryReportItem, ProjectionReportItem
from src.domain.repositories.movement_repository import MovementRepository
from src.domain.repositories.inventory_repository import InventoryRepository
from src.domain.entities.movement import MovementType
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

class ReportUseCase:
    def __init__(self, movement_repo: MovementRepository, inv_repo: InventoryRepository):
        self.movement_repo = movement_repo
        self.inv_repo = inv_repo

    async def get_sales_report(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> SalesReportResponse:
        logger.info("Generando reporte de ventas", date_from=date_from, date_to=date_to)
        
        sales = await self.movement_repo.get_all(type_movement=MovementType.SELL, date_from=date_from, date_to=date_to)
        
        items = []
        total_revenue = Decimal('0.0')
        total_profit = Decimal('0.0')

        # Para calcular profit necesitamos el last_purchase_price *antes* o de esa fecha
        # Simplificación: usar get_last_purchase_by_inventory actual. En un sistema real
        # se debe registrar el coste de la mercancía vendida (COGS) en el momento de la venta.
        # Aquí calcularemos con la última compra actual para seguir la instrucción.
        
        for sale in sales:
            last_purchase = await self.movement_repo.get_last_purchase_by_inventory(sale.id_inventory)
            last_purchase_price = last_purchase.value if last_purchase else Decimal('0.0')
            
            profit = (sale.value - last_purchase_price) * sale.quantity
            total_revenue += sale.value * sale.quantity
            total_profit += profit

            items.append(SaleReportItem(
                id_movement=sale.id_movement,
                date=sale.date,
                id_inventory=sale.id_inventory,
                quantity=sale.quantity,
                value_sell=sale.value,
                last_purchase_price=last_purchase_price,
                profit=profit
            ))

        return SalesReportResponse(
            items=items,
            total_revenue=total_revenue,
            total_profit=total_profit
        )

    async def get_inventory_report(self) -> List[InventoryReportItem]:
        logger.info("Generando reporte de existencias")
        # Obtiene todos los movimientos
        movements = await self.movement_repo.get_all()
        
        inventory_data = defaultdict(lambda: {"bought": 0, "sold": 0})
        
        for mov in movements:
            if mov.type_movement == MovementType.BUY:
                inventory_data[mov.id_inventory]["bought"] += mov.quantity
            elif mov.type_movement == MovementType.SELL:
                inventory_data[mov.id_inventory]["sold"] += mov.quantity
                
        reports = []
        for id_inv, data in inventory_data.items():
            reports.append(InventoryReportItem(
                id_inventory=id_inv,
                total_bought=data["bought"],
                total_sold=data["sold"],
                current_stock=data["bought"] - data["sold"]
            ))
            
        return reports

    async def get_projection_report(self) -> List[ProjectionReportItem]:
        logger.info("Generando reporte de proyecciones")
        # Promedio de ventas de los últimos 3 meses
        date_from = datetime.now() - timedelta(days=90)
        sales = await self.movement_repo.get_all(type_movement=MovementType.SELL, date_from=date_from)
        
        sales_by_inv = defaultdict(int)
        for sale in sales:
            sales_by_inv[sale.id_inventory] += sale.quantity
            
        reports = []
        for id_inv, total_sold in sales_by_inv.items():
            # Promedio mensual = total_sold / 3
            avg = Decimal(total_sold) / Decimal('3.0')
            reports.append(ProjectionReportItem(
                id_inventory=id_inv,
                average_monthly_sales=avg,
                projected_sales_next_month=int(round(avg, 0))
            ))
            
        return reports
