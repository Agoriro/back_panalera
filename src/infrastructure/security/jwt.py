# Paso 13: src/infrastructure/security/jwt.py
"""
Módulo para la creación y verificación de JSON Web Tokens (JWT).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.shared.config.settings import settings
from src.shared.exceptions.domain_exceptions import UnauthorizedException


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea un access token de corta duración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Crea un refresh token de larga duración."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    Lanza UnauthorizedException si el token es inválido o ha expirado.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise UnauthorizedException("No se pudieron validar las credenciales") from None
