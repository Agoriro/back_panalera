# Paso 15: src/application/use_cases/catalog_use_case.py
from typing import List, TypeVar, Type, Generic
from uuid import UUID
from pydantic import BaseModel

from src.domain.repositories.catalog_repository import BaseCatalogRepository
from src.shared.exceptions.domain_exceptions import ResourceNotFoundException, ResourceAlreadyExistsException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

T_Entity = TypeVar('T_Entity')
T_CreateDTO = TypeVar('T_CreateDTO', bound=BaseModel)
T_UpdateDTO = TypeVar('T_UpdateDTO', bound=BaseModel)
T_ResponseDTO = TypeVar('T_ResponseDTO', bound=BaseModel)

class CatalogUseCase(Generic[T_Entity, T_CreateDTO, T_UpdateDTO, T_ResponseDTO]):
    def __init__(self, repo: BaseCatalogRepository[T_Entity], entity_cls: Type[T_Entity], response_dto_cls: Type[T_ResponseDTO], name_field: str):
        self.repo = repo
        self.entity_cls = entity_cls
        self.response_dto_cls = response_dto_cls
        self.name_field = name_field

    async def create(self, data: T_CreateDTO) -> T_ResponseDTO:
        name_val = getattr(data, self.name_field, None)
        logger.info(f"Creando entidad de catálogo", name=name_val)
        
        if name_val:
            existing = await self.repo.get_by_name(name_val)
            if existing:
                raise ResourceAlreadyExistsException(f"El recurso con nombre {name_val} ya existe")
        
        entity_dict = data.model_dump()
        # id es generado por BD, lo omitimos en la instanciación pero dataclasses requiere todos los campos posicionales a menos que tengan default
        # usaremos un hack para inyectar None en el id
        id_field = f"id_{self.entity_cls.__name__.lower()}"
        entity_dict[id_field] = None
        
        entity = self.entity_cls(**entity_dict)
        created_entity = await self.repo.create(entity)
        return self.response_dto_cls.model_validate(created_entity)

    async def get_all(self) -> List[T_ResponseDTO]:
        entities = await self.repo.get_all()
        return [self.response_dto_cls.model_validate(e) for e in entities]

    async def get_by_id(self, id: UUID) -> T_ResponseDTO:
        entity = await self.repo.get_by_id(id)
        if not entity:
            raise ResourceNotFoundException("Recurso no encontrado")
        return self.response_dto_cls.model_validate(entity)

    async def update(self, id: UUID, data: T_UpdateDTO) -> T_ResponseDTO:
        entity = await self.repo.get_by_id(id)
        if not entity:
            raise ResourceNotFoundException("Recurso no encontrado")

        name_val = getattr(data, self.name_field, None)
        if name_val:
            existing = await self.repo.get_by_name(name_val)
            id_field = f"id_{self.entity_cls.__name__.lower()}"
            existing_id = getattr(existing, id_field, None) if existing else None
            
            if existing and existing_id != id:
                raise ResourceAlreadyExistsException(f"El recurso con nombre {name_val} ya existe")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
            
        updated_entity = await self.repo.update(entity)
        return self.response_dto_cls.model_validate(updated_entity)

    async def toggle_active(self, id: UUID) -> T_ResponseDTO:
        entity = await self.repo.get_by_id(id)
        if not entity:
            raise ResourceNotFoundException("Recurso no encontrado")
            
        if hasattr(entity, 'is_active'):
            entity.is_active = not entity.is_active # type: ignore
            updated_entity = await self.repo.update(entity)
            return self.response_dto_cls.model_validate(updated_entity)
        else:
            return self.response_dto_cls.model_validate(entity)
