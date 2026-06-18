# Paso 16: src/interfaces/api/v1/routers/auth.py
from fastapi import APIRouter, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from src.application.dtos.auth_dto import LoginRequest, RefreshRequest, TokenResponse
from src.application.use_cases.auth_use_case import AuthUseCase
from src.interfaces.api.dependencies.use_cases import get_auth_use_case

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, use_case: AuthUseCase = Depends(get_auth_use_case)):
    """Inicia sesión y devuelve un token de acceso y un token de refresco."""
    return await use_case.login(data)

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("5/minute")
async def refresh(request: Request, data: RefreshRequest, use_case: AuthUseCase = Depends(get_auth_use_case)):
    """Renueva el token de acceso utilizando un token de refresco válido."""
    return await use_case.refresh(data)
