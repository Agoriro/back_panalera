# Paso 15: src/application/use_cases/auth_use_case.py
from uuid import UUID

from src.application.dtos.auth_dto import LoginRequest, RefreshRequest, TokenResponse
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.infrastructure.security.password import verify_password
from src.shared.exceptions.domain_exceptions import UnauthorizedException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, data: LoginRequest) -> TokenResponse:
        logger.info("Intento de login", username=data.username)
        user = await self.user_repo.get_by_username(data.username)

        if not user or not user.is_active:
            logger.warning(
                "Login fallido: usuario no existe o inactivo", username=data.username
            )
            raise UnauthorizedException("Credenciales inválidas")

        if not verify_password(data.password, user.password):
            logger.warning(
                "Login fallido: contraseña incorrecta", username=data.username
            )
            raise UnauthorizedException("Credenciales inválidas")

        # El token incluye el rol como string legible
        token_data = {"sub": str(user.id_user), "role": user.role_name or ""}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(
            data={"sub": str(user.id_user), "ver": user.token_version}
        )

        logger.info("Login exitoso", username=data.username)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        payload = verify_token(data.refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        token_version = payload.get("ver")
        if not user_id or not isinstance(token_version, int):
            raise UnauthorizedException("Token inválido")

        try:
            parsed_user_id = UUID(user_id)
        except (TypeError, ValueError):
            raise UnauthorizedException("Token inválido") from None

        user = await self.user_repo.rotate_token_version(parsed_user_id, token_version)
        if not user or not user.is_active:
            raise UnauthorizedException("Usuario inactivo o no encontrado")

        token_data = {"sub": str(user.id_user), "role": user.role_name or ""}
        access_token = create_access_token(data=token_data)

        refresh_token = create_refresh_token(
            data={"sub": str(user.id_user), "ver": user.token_version}
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
