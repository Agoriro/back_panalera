# Paso 16: src/interfaces/api/v1/routers/inventory.py
from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID

from src.application.dtos.inventory_dto import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryPhotoCreate, InventoryPhotoResponse
from src.application.use_cases.inventory_use_case import InventoryUseCase
from src.interfaces.api.dependencies.use_cases import get_inventory_use_case
from src.interfaces.api.dependencies.auth import is_authenticated

router = APIRouter(prefix="/inventory", tags=["Inventory"], dependencies=[Depends(is_authenticated)])

@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(data: InventoryCreate, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return await use_case.create(data)

@router.get("", response_model=List[InventoryResponse])
async def get_inventories(
    category: Optional[UUID] = None,
    gender: Optional[UUID] = None,
    color: Optional[UUID] = None,
    size: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    code_inventory: Optional[str] = None,
    barcode_inventory: Optional[str] = None,
    search: Optional[str] = Query(None, description="Búsqueda parcial en descripción, código o código de barras"),
    use_case: InventoryUseCase = Depends(get_inventory_use_case)
):
    return await use_case.get_all(category, gender, color, size, is_active, code_inventory, barcode_inventory, search)

@router.get("/{id}", response_model=InventoryResponse)
async def get_inventory(id: UUID, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return await use_case.get_by_id(id)

@router.put("/{id}", response_model=InventoryResponse)
async def update_inventory(id: UUID, data: InventoryUpdate, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return await use_case.update(id, data)

@router.patch("/{id}/toggle", response_model=InventoryResponse)
async def toggle_inventory(id: UUID, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return await use_case.toggle_active(id)

@router.post("/{id}/photos", response_model=List[InventoryPhotoResponse], status_code=status.HTTP_201_CREATED)
async def add_inventory_photos(id: UUID, data: InventoryPhotoCreate, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return await use_case.add_photos(id, data)

@router.delete("/{id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_photo(id: UUID, photo_id: UUID, use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    await use_case.delete_photo(id, photo_id)
    return None
