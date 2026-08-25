# Paso 17: src/interfaces/api/dependencies/use_cases.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# DTOs para Catalog
from src.application.dtos.catalog_dto import (
    BasicCatalogCreate,
    BasicCatalogUpdate,
    CategoryResponse,
    ColorResponse,
    GenderResponse,
    SizeResponse,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

# Casos de uso
from src.application.use_cases.auth_use_case import AuthUseCase
from src.application.use_cases.catalog_use_case import CatalogUseCase
from src.application.use_cases.inventory_use_case import InventoryUseCase
from src.application.use_cases.movement_use_case import MovementUseCase
from src.application.use_cases.report_use_case import ReportUseCase
from src.application.use_cases.role_use_case import RoleUseCase
from src.application.use_cases.user_use_case import UserUseCase
from src.domain.entities.catalog import Category, Color, Gender, Size, Supplier
from src.infrastructure.database.repositories.catalog_repository import (
    CategoryRepository,
    ColorRepository,
    GenderRepository,
    SizeRepository,
    SupplierRepository,
)
from src.infrastructure.database.repositories.inventory_repository import (
    InventoryPhotoRepository,
    InventoryRepository,
)
from src.infrastructure.database.repositories.movement_repository import (
    MovementRepository,
)

# Repositorios
from src.infrastructure.database.repositories.role_repository import RoleRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.interfaces.api.dependencies.database import get_db_session


def get_auth_use_case(session: AsyncSession = Depends(get_db_session)) -> AuthUseCase:
    return AuthUseCase(UserRepository(session))


def get_role_use_case(session: AsyncSession = Depends(get_db_session)) -> RoleUseCase:
    return RoleUseCase(RoleRepository(session))


def get_user_use_case(session: AsyncSession = Depends(get_db_session)) -> UserUseCase:
    return UserUseCase(UserRepository(session), RoleRepository(session))


# --- Catalog Use Cases ---
def get_supplier_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogUseCase:
    return CatalogUseCase[Supplier, SupplierCreate, SupplierUpdate, SupplierResponse](
        SupplierRepository(session), Supplier, SupplierResponse, "name_supplier"
    )


def get_color_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogUseCase:
    return CatalogUseCase[Color, BasicCatalogCreate, BasicCatalogUpdate, ColorResponse](
        ColorRepository(session), Color, ColorResponse, "name_color"
    )


def get_size_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogUseCase:
    return CatalogUseCase[Size, BasicCatalogCreate, BasicCatalogUpdate, SizeResponse](
        SizeRepository(session), Size, SizeResponse, "name_size"
    )


def get_category_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogUseCase:
    return CatalogUseCase[
        Category, BasicCatalogCreate, BasicCatalogUpdate, CategoryResponse
    ](CategoryRepository(session), Category, CategoryResponse, "name_category")


def get_gender_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogUseCase:
    return CatalogUseCase[
        Gender, BasicCatalogCreate, BasicCatalogUpdate, GenderResponse
    ](GenderRepository(session), Gender, GenderResponse, "name_gender")


# --- Inventory, Movements, Reports ---
def get_inventory_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> InventoryUseCase:
    return InventoryUseCase(
        InventoryRepository(session),
        InventoryPhotoRepository(session),
        SupplierRepository(session),
        ColorRepository(session),
        SizeRepository(session),
        CategoryRepository(session),
        GenderRepository(session),
    )


def get_movement_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> MovementUseCase:
    return MovementUseCase(
        MovementRepository(session),
        InventoryRepository(session),
        SupplierRepository(session),
    )


def get_report_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ReportUseCase:
    return ReportUseCase(MovementRepository(session))
