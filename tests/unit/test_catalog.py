import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.use_cases.catalog_use_case import CatalogUseCase
from src.application.dtos.catalog_dto import BasicCatalogCreate, BasicCatalogUpdate, CategoryResponse
from src.domain.entities.catalog import Category

@pytest.mark.asyncio
async def test_create_category_with_generic_name():
    repo = AsyncMock()
    repo.get_by_name.return_value = None
    
    created_id = uuid4()
    repo.create.side_effect = lambda entity: Category(id_category=created_id, name_category=entity.name_category)
    
    use_case = CatalogUseCase[Category, BasicCatalogCreate, BasicCatalogUpdate, CategoryResponse](
        repo=repo,
        entity_cls=Category,
        response_dto_cls=CategoryResponse,
        name_field="name_category"
    )
    
    data = BasicCatalogCreate(name="Pañales")
    response = await use_case.create(data)
    
    assert response.id_category == created_id
    assert response.name_category == "Pañales"
    repo.create.assert_called_once()
    created_arg = repo.create.call_args[0][0]
    assert isinstance(created_arg, Category)
    assert created_arg.name_category == "Pañales"

@pytest.mark.asyncio
async def test_create_category_with_specific_name_category():
    repo = AsyncMock()
    repo.get_by_name.return_value = None
    
    created_id = uuid4()
    repo.create.side_effect = lambda entity: Category(id_category=created_id, name_category=entity.name_category)
    
    use_case = CatalogUseCase[Category, BasicCatalogCreate, BasicCatalogUpdate, CategoryResponse](
        repo=repo,
        entity_cls=Category,
        response_dto_cls=CategoryResponse,
        name_field="name_category"
    )
    
    data = BasicCatalogCreate(name_category="Ropa Bebé")
    response = await use_case.create(data)
    
    assert response.id_category == created_id
    assert response.name_category == "Ropa Bebé"

@pytest.mark.asyncio
async def test_update_category_with_generic_name():
    repo = AsyncMock()
    cat_id = uuid4()
    existing_category = Category(id_category=cat_id, name_category="Old Name")
    repo.get_by_id.return_value = existing_category
    repo.get_by_name.return_value = None
    repo.update.side_effect = lambda entity: entity
    
    use_case = CatalogUseCase[Category, BasicCatalogCreate, BasicCatalogUpdate, CategoryResponse](
        repo=repo,
        entity_cls=Category,
        response_dto_cls=CategoryResponse,
        name_field="name_category"
    )
    
    data = BasicCatalogUpdate(name="New Name")
    response = await use_case.update(cat_id, data)
    
    assert response.name_category == "New Name"
