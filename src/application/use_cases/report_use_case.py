from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.application.date_ranges import normalize_date_range
from src.application.dtos.report_dto import (
    InventoryReportItem,
    ProjectionReportItem,
    SaleReportItem,
    SalesReportResponse,
)
from src.domain.repositories.movement_repository import MovementRepository
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ReportUseCase:
    def __init__(self, movement_repo: MovementRepository):
        self.movement_repo = movement_repo

    async def get_sales_report(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> SalesReportResponse:
        logger.info("Generando reporte de ventas", date_from=date_from, date_to=date_to)
        date_from, date_to = normalize_date_range(date_from, date_to)
        (
            sales,
            total,
            total_revenue,
            total_profit,
        ) = await self.movement_repo.get_sales_report(
            date_from,
            date_to,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        items = [
            SaleReportItem(
                id_movement=sale.id_movement,
                date=sale.date,
                id_inventory=sale.id_inventory,
                quantity=sale.quantity,
                value_sell=sale.value,
                last_purchase_price=sale.unit_cost,
                profit=(sale.value - sale.unit_cost) * sale.quantity,
            )
            for sale in sales
        ]
        return SalesReportResponse(
            items=items,
            total_revenue=total_revenue,
            total_profit=total_profit,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    async def get_inventory_report(self) -> list[InventoryReportItem]:
        logger.info("Generando reporte de existencias")
        rows = await self.movement_repo.get_inventory_report()
        return [
            InventoryReportItem(
                id_inventory=id_inventory,
                total_bought=total_bought,
                total_sold=total_sold,
                current_stock=current_stock,
            )
            for id_inventory, total_bought, total_sold, current_stock in rows
        ]

    async def get_projection_report(self) -> list[ProjectionReportItem]:
        logger.info("Generando reporte de proyecciones")
        date_from = datetime.now(UTC) - timedelta(days=90)
        rows = await self.movement_repo.get_projection_report(date_from)
        reports = []
        for id_inv, total_sold in rows:
            average = Decimal(total_sold) / Decimal("3.0")
            reports.append(
                ProjectionReportItem(
                    id_inventory=id_inv,
                    average_monthly_sales=average,
                    projected_sales_next_month=int(round(average, 0)),
                )
            )
        return reports
