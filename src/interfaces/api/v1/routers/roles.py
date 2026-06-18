# Paso 16: src/interfaces/api/v1/routers/roles.py
from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.application.dtos.role_dto import RoleCreate, RoleUpdate, RoleResponse
from src.application.use_cases.role_use_case import RoleUseCase
from src.interfaces.api.dependencies.use_cases import get_role_use_case
from src.interfaces.api.dependencies.auth import is_authenticated, has_role

router = APIRouter(prefix="/roles", tags=["Roles"], dependencies=[Depends(is_authenticated)])

@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(has_role("admin"))])
async def create_role(data: RoleCreate, use_case: RoleUseCase = Depends(get_role_use_case)):
    """Crea un nuevo rol (Solo Admin)."""
    return await use_case.create(data)

@router.get("", response_model=List[RoleResponse])
async def get_roles(use_case: RoleUseCase = Depends(get_role_use_case)):
    """Lista todos los roles disponibles."""
    return await use_case.get_all()

@router.get("/{id}", response_model=RoleResponse)
async def get_role(id: UUID, use_case: RoleUseCase = Depends(get_role_use_case)):
    """Obtiene un rol por su ID."""
    return await use_case.get_by_id(id)

@router.put("/{id}", response_model=RoleResponse, dependencies=[Depends(has_role("admin"))])
async def update_role(id: UUID, data: RoleUpdate, use_case: RoleUseCase = Depends(get_role_use_case)):
    """Actualiza un rol existente (Solo Admin)."""
    return await use_case.update(id, data)
