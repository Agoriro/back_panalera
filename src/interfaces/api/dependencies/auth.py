# Paso 17: src/interfaces/api/dependencies/auth.py
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from src.infrastructure.security.jwt import verify_token
from src.shared.exceptions.domain_exceptions import UnauthorizedException, ForbiddenException

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
        payload: Dict[str, Any] = Depends(is_authenticated)
    ):
        role_name = payload.get("role")
        if not role_name:
            raise ForbiddenException("Rol no especificado en el token")
            
        if role_name.lower() != required_role.lower():
            raise ForbiddenException(f"Requiere el rol: {required_role}")
            
        return True
    return role_checker
