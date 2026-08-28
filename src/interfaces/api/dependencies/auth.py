# Paso 17: src/interfaces/api/dependencies/auth.py
from enum import StrEnum
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

security = HTTPBearer(auto_error=False)


class Permission(StrEnum):
    READ_DATA = "read:data"
    MANAGE_USERS = "manage:users"
    MANAGE_ROLES = "manage:roles"
    MANAGE_CATALOG = "manage:catalog"
    WRITE_INVENTORY = "write:inventory"
    WRITE_MOVEMENTS = "write:movements"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "admin": frozenset(Permission),
    "operator": frozenset(
        {
            Permission.READ_DATA,
            Permission.WRITE_INVENTORY,
            Permission.WRITE_MOVEMENTS,
        }
    ),
    "consulta": frozenset({Permission.READ_DATA}),
}


def get_auth_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    return UserRepository(session)


async def is_authenticated(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    user_repo: IUserRepository = Depends(get_auth_user_repository),
) -> dict[str, Any]:
    """Dependencia que valida que el usuario está autenticado y devuelve el payload del token."""
    if credentials is None:
        raise UnauthorizedException("Credenciales no proporcionadas")
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


def has_permission(required_permission: Permission):
    """Valida permisos derivados del rol vigente consultado en DB."""

    async def permission_checker(
        payload: dict[str, Any] = Depends(is_authenticated),
    ) -> bool:
        role_name = str(payload.get("role", "")).strip().casefold()
        permissions = ROLE_PERMISSIONS.get(role_name, frozenset())
        if required_permission not in permissions:
            raise ForbiddenException(f"Requiere permiso: {required_permission.value}")
        return True

    return permission_checker
