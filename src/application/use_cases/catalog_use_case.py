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

    def _extract_name(self, data: BaseModel) -> str:
        if hasattr(data, "get_name"):
            return getattr(data, "get_name")()
        return getattr(data, self.name_field, None) or getattr(data, "name", None) or ""

    async def create(self, data: T_CreateDTO) -> T_ResponseDTO:
        name_val = self._extract_name(data)
        logger.info("Creando entidad de catálogo", entity=self.entity_cls.__name__, name=name_val)
        
        if name_val:
            existing = await self.repo.get_by_name(name_val)
            if existing:
                raise ResourceAlreadyExistsException(f"El recurso con nombre '{name_val}' ya existe")
        
        entity_dict = data.model_dump(exclude_unset=True)
        
        # Mapear campo genérico 'name' al nombre de campo específico de la entidad
        if "name" in entity_dict:
            entity_dict[self.name_field] = entity_dict.pop("name")

        # Limpiar cualquier otro campo name_* que no pertenezca a esta entidad
        for field in ["name_category", "name_color", "name_size", "name_gender", "name_supplier"]:
            if field != self.name_field and field in entity_dict:
                entity_dict.pop(field)

        if name_val and self.name_field not in entity_dict:
            entity_dict[self.name_field] = name_val

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

        name_val = self._extract_name(data)
        if name_val:
            existing = await self.repo.get_by_name(name_val)
            id_field = f"id_{self.entity_cls.__name__.lower()}"
            existing_id = getattr(existing, id_field, None) if existing else None
            
            if existing and existing_id != id:
                raise ResourceAlreadyExistsException(f"El recurso con nombre '{name_val}' ya existe")

        data_dict = data.model_dump(exclude_unset=True)
        if "name" in data_dict:
            data_dict[self.name_field] = data_dict.pop("name")

        for field in ["name_category", "name_color", "name_size", "name_gender", "name_supplier"]:
            if field != self.name_field and field in data_dict:
                data_dict.pop(field)

        for key, value in data_dict.items():
            if hasattr(entity, key):
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
