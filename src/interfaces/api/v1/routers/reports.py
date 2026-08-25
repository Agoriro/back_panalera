# Paso 16: src/interfaces/api/v1/routers/reports.py
from datetime import datetime

from fastapi import APIRouter, Depends

from src.application.dtos.report_dto import (
    InventoryReportItem,
    ProjectionReportItem,
    SalesReportResponse,
)
from src.application.use_cases.report_use_case import ReportUseCase
from src.interfaces.api.dependencies.auth import is_authenticated
from src.interfaces.api.dependencies.use_cases import get_report_use_case

router = APIRouter(
    prefix="/reports", tags=["Reports"], dependencies=[Depends(is_authenticated)]
)


@router.get("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    use_case: ReportUseCase = Depends(get_report_use_case),
):
    """Genera un reporte de ventas en un periodo determinado."""
    return await use_case.get_sales_report(date_from, date_to)


@router.get("/inventory", response_model=list[InventoryReportItem])
async def get_inventory_report(use_case: ReportUseCase = Depends(get_report_use_case)):
    """Genera un reporte de existencias actuales por producto."""
    return await use_case.get_inventory_report()


@router.get("/projection", response_model=list[ProjectionReportItem])
async def get_projection_report(use_case: ReportUseCase = Depends(get_report_use_case)):
    """Genera un reporte de proyección de ventas."""
    return await use_case.get_projection_report()
