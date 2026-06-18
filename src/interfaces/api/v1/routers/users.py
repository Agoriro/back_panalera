# Paso 16: src/interfaces/api/v1/routers/users.py
from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.application.dtos.user_dto import UserCreate, UserUpdate, UserResponse
from src.application.use_cases.user_use_case import UserUseCase
from src.interfaces.api.dependencies.use_cases import get_user_use_case
from src.interfaces.api.dependencies.auth import is_authenticated, has_role

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(is_authenticated)])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(has_role("admin"))])
async def create_user(data: UserCreate, use_case: UserUseCase = Depends(get_user_use_case)):
    """Crea un nuevo usuario (Solo Admin)."""
    return await use_case.create(data)

@router.get("", response_model=List[UserResponse])
async def get_users(use_case: UserUseCase = Depends(get_user_use_case)):
    """Lista todos los usuarios."""
    return await use_case.get_all()

@router.get("/{id}", response_model=UserResponse)
async def get_user(id: UUID, use_case: UserUseCase = Depends(get_user_use_case)):
    """Obtiene un usuario por su ID."""
    return await use_case.get_by_id(id)

@router.put("/{id}", response_model=UserResponse, dependencies=[Depends(has_role("admin"))])
async def update_user(id: UUID, data: UserUpdate, use_case: UserUseCase = Depends(get_user_use_case)):
    """Actualiza un usuario existente (Solo Admin)."""
    return await use_case.update(id, data)

@router.patch("/{id}/toggle", response_model=UserResponse, dependencies=[Depends(has_role("admin"))])
async def toggle_user_active(id: UUID, use_case: UserUseCase = Depends(get_user_use_case)):
    """Activa o desactiva un usuario (Solo Admin)."""
    return await use_case.toggle_active(id)
