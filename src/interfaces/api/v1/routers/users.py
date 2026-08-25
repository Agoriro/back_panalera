# Paso 16: src/interfaces/api/v1/routers/users.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.pagination_dto import Page
from src.application.dtos.user_dto import UserCreate, UserResponse, UserUpdate
from src.application.use_cases.user_use_case import UserUseCase
from src.interfaces.api.dependencies.auth import Permission, has_permission
from src.interfaces.api.dependencies.use_cases import get_user_use_case

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(has_permission(Permission.MANAGE_USERS))],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate, use_case: UserUseCase = Depends(get_user_use_case)
):
    """Crea un nuevo usuario (Solo Admin)."""
    return await use_case.create(data)


@router.get("", response_model=Page[UserResponse])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    use_case: UserUseCase = Depends(get_user_use_case),
):
    """Lista todos los usuarios."""
    return await use_case.get_all(page, page_size)


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: UUID, use_case: UserUseCase = Depends(get_user_use_case)):
    """Obtiene un usuario por su ID."""
    return await use_case.get_by_id(id)


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: UUID, data: UserUpdate, use_case: UserUseCase = Depends(get_user_use_case)
):
    """Actualiza un usuario existente (Solo Admin)."""
    return await use_case.update(id, data)


@router.patch(
    "/{id}/toggle",
    response_model=UserResponse,
)
async def toggle_user_active(
    id: UUID, use_case: UserUseCase = Depends(get_user_use_case)
):
    """Activa o desactiva un usuario (Solo Admin)."""
    return await use_case.toggle_active(id)
