# Paso 15: src/application/use_cases/role_use_case.py
from typing import List
from uuid import UUID
from src.application.dtos.role_dto import RoleCreate, RoleUpdate, RoleResponse
from src.domain.entities.role import Role
from src.domain.repositories.role_repository import RoleRepository
from src.shared.exceptions.domain_exceptions import ResourceNotFoundException, ResourceAlreadyExistsException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

class RoleUseCase:
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    async def create(self, data: RoleCreate) -> RoleResponse:
        logger.info("Creando rol", name=data.name)
        existing = await self.role_repo.get_by_name(data.name)
        if existing:
            raise ResourceAlreadyExistsException(f"El rol {data.name} ya existe")
            
        role = Role(id_role=None, name=data.name) # type: ignore
        created_role = await self.role_repo.create(role)
        logger.info("Rol creado exitosamente", id=str(created_role.id_role))
        return RoleResponse.model_validate(created_role)

    async def get_all(self) -> List[RoleResponse]:
        roles = await self.role_repo.get_all()
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_by_id(self, id_role: UUID) -> RoleResponse:
        role = await self.role_repo.get_by_id(id_role)
        if not role:
            raise ResourceNotFoundException("Rol no encontrado")
        return RoleResponse.model_validate(role)

    async def update(self, id_role: UUID, data: RoleUpdate) -> RoleResponse:
        logger.info("Actualizando rol", id=str(id_role))
        role = await self.role_repo.get_by_id(id_role)
        if not role:
            raise ResourceNotFoundException("Rol no encontrado")
            
        existing = await self.role_repo.get_by_name(data.name)
        if existing and existing.id_role != id_role:
            raise ResourceAlreadyExistsException(f"El rol {data.name} ya existe")

        role.name = data.name
        updated_role = await self.role_repo.update(role)
        return RoleResponse.model_validate(updated_role)
