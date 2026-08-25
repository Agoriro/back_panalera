# Paso 17: src/interfaces/api/dependencies/auth.py
from typing import Any
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.user_repository import UserRepository as IUserRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt import verify_token
from src.interfaces.api.dependencies.database import get_db_session
from src.shared.exceptions.domain_exceptions import (
    ForbiddenException,
    UnauthorizedException,
)

security = HTTPBearer()


def get_auth_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    return UserRepository(session)


async def is_authenticated(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: IUserRepository = Depends(get_auth_user_repository),
) -> dict[str, Any]:
    """Dependencia que valida que el usuario está autenticado y devuelve el payload del token."""
    token = credentials.credentials
    try:
        payload = verify_token(token, expected_type="access")
        user_id = UUID(payload["sub"])
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Usuario inactivo o no encontrado")

        authenticated_payload = payload.copy()
        authenticated_payload["sub"] = str(user.id_user)
        authenticated_payload["role"] = user.role_name or ""
        return authenticated_payload
    except (KeyError, TypeError, ValueError):
        raise UnauthorizedException("Token inválido") from None
    except UnauthorizedException:
        raise


def has_role(required_role: str):
    """Fábrica de dependencias que valida si el usuario tiene un rol específico."""

    async def role_checker(payload: dict[str, Any] = Depends(is_authenticated)):
        role_name = payload.get("role")
        if not role_name:
            raise ForbiddenException("Rol no especificado en el token")

        if role_name.lower() != required_role.lower():
            raise ForbiddenException(f"Requiere el rol: {required_role}")

        return True

    return role_checker
