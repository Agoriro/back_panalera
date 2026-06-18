# Paso 15: src/application/use_cases/user_use_case.py
from typing import List
from uuid import UUID
from src.application.dtos.user_dto import UserCreate, UserUpdate, UserResponse
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.role_repository import RoleRepository
from src.infrastructure.security.password import get_password_hash
from src.shared.exceptions.domain_exceptions import ResourceNotFoundException, ResourceAlreadyExistsException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

class UserUseCase:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def create(self, data: UserCreate) -> UserResponse:
        logger.info("Creando usuario", username=data.user)
        existing = await self.user_repo.get_by_username(data.user)
        if existing:
            raise ResourceAlreadyExistsException(f"El usuario {data.user} ya existe")
            
        role = await self.role_repo.get_by_id(data.id_role)
        if not role:
            raise ResourceNotFoundException("Rol no encontrado")

        hashed_password = get_password_hash(data.password)
        user = User(
            id_user=None, # type: ignore
            user=data.user,
            password=hashed_password,
            id_role=data.id_role,
            is_active=True
        )
        
        created_user = await self.user_repo.create(user)
        logger.info("Usuario creado exitosamente", id=str(created_user.id_user))
        return UserResponse.model_validate(created_user)

    async def get_all(self) -> List[UserResponse]:
        users = await self.user_repo.get_all()
        return [UserResponse.model_validate(u) for u in users]

    async def get_by_id(self, id_user: UUID) -> UserResponse:
        user = await self.user_repo.get_by_id(id_user)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado")
        return UserResponse.model_validate(user)

    async def update(self, id_user: UUID, data: UserUpdate) -> UserResponse:
        logger.info("Actualizando usuario", id=str(id_user))
        user = await self.user_repo.get_by_id(id_user)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado")

        if data.user:
            existing = await self.user_repo.get_by_username(data.user)
            if existing and existing.id_user != id_user:
                raise ResourceAlreadyExistsException(f"El usuario {data.user} ya existe")
            user.user = data.user
            
        if data.id_role:
            role = await self.role_repo.get_by_id(data.id_role)
            if not role:
                raise ResourceNotFoundException("Rol no encontrado")
            user.id_role = data.id_role

        updated_user = await self.user_repo.update(user)
        return UserResponse.model_validate(updated_user)

    async def toggle_active(self, id_user: UUID) -> UserResponse:
        logger.info("Cambiando estado de usuario", id=str(id_user))
        user = await self.user_repo.get_by_id(id_user)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado")
            
        user.is_active = not user.is_active
        updated_user = await self.user_repo.update(user)
        return UserResponse.model_validate(updated_user)
