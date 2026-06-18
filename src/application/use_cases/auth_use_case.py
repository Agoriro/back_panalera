# Paso 15: src/application/use_cases/auth_use_case.py
from src.application.dtos.auth_dto import LoginRequest, TokenResponse, RefreshRequest
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.security.password import verify_password
from src.infrastructure.security.jwt import create_access_token, create_refresh_token, verify_token
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
            logger.warning("Login fallido: usuario no existe o inactivo", username=data.username)
            raise UnauthorizedException("Credenciales inválidas")

        if not verify_password(data.password, user.password):
            logger.warning("Login fallido: contraseña incorrecta", username=data.username)
            raise UnauthorizedException("Credenciales inválidas")

        # El token incluye el rol
        token_data = {"sub": str(user.id_user), "role": str(user.id_role)}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data={"sub": str(user.id_user)})

        logger.info("Login exitoso", username=data.username)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        payload = verify_token(data.refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Token inválido")
            
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Usuario inactivo o no encontrado")

        token_data = {"sub": str(user.id_user), "role": str(user.id_role)}
        access_token = create_access_token(data=token_data)
        
        return TokenResponse(access_token=access_token, refresh_token=data.refresh_token)
