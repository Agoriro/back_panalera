# Paso 17: src/interfaces/api/dependencies/auth.py
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from src.infrastructure.security.jwt import verify_token
from src.shared.exceptions.domain_exceptions import UnauthorizedException, ForbiddenException
from src.application.use_cases.role_use_case import RoleUseCase
from src.interfaces.api.dependencies.use_cases import get_role_use_case

security = HTTPBearer()

async def is_authenticated(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependencia que valida que el usuario está autenticado y devuelve el payload del token."""
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return payload
    except UnauthorizedException:
        raise

def has_role(required_role: str):
    """Fábrica de dependencias que valida si el usuario tiene un rol específico."""
    async def role_checker(
        payload: Dict[str, Any] = Depends(is_authenticated),
        role_use_case: RoleUseCase = Depends(get_role_use_case)
    ):
        role_id_str = payload.get("role")
        if not role_id_str:
            raise ForbiddenException("Rol no especificado en el token")
            
        try:
            role = await role_use_case.get_by_id(role_id_str) # type: ignore
            if role.name.lower() != required_role.lower():
                raise ForbiddenException(f"Requiere el rol: {required_role}")
        except Exception:
            raise ForbiddenException(f"Requiere el rol: {required_role}")
            
        return True
    return role_checker
