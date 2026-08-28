# Paso 16: src/interfaces/api/v1/routers/catalog.py
from uuid import UUID

from fastapi import APIRouter, Depends, status

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
from src.application.use_cases.catalog_use_case import CatalogUseCase
from src.interfaces.api.dependencies.auth import Permission, has_permission
from src.interfaces.api.dependencies.use_cases import (
    get_category_use_case,
    get_color_use_case,
    get_gender_use_case,
    get_size_use_case,
    get_supplier_use_case,
)

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
    dependencies=[Depends(has_permission(Permission.READ_DATA))],
)


# --- Suppliers ---
@router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def create_supplier(
    data: SupplierCreate, use_case: CatalogUseCase = Depends(get_supplier_use_case)
):
    return await use_case.create(data)


@router.get("/suppliers", response_model=list[SupplierResponse])
async def get_suppliers(use_case: CatalogUseCase = Depends(get_supplier_use_case)):
    return await use_case.get_all()


@router.get("/suppliers/{id}", response_model=SupplierResponse)
async def get_supplier(
    id: UUID, use_case: CatalogUseCase = Depends(get_supplier_use_case)
):
    return await use_case.get_by_id(id)


@router.put(
    "/suppliers/{id}",
    response_model=SupplierResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def update_supplier(
    id: UUID,
    data: SupplierUpdate,
    use_case: CatalogUseCase = Depends(get_supplier_use_case),
):
    return await use_case.update(id, data)


@router.patch(
    "/suppliers/{id}/toggle",
    response_model=SupplierResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def toggle_supplier(
    id: UUID, use_case: CatalogUseCase = Depends(get_supplier_use_case)
):
    return await use_case.toggle_active(id)


# --- Colors ---
@router.post(
    "/colors",
    response_model=ColorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def create_color(
    data: BasicCatalogCreate, use_case: CatalogUseCase = Depends(get_color_use_case)
):
    return await use_case.create(data)


@router.get("/colors", response_model=list[ColorResponse])
async def get_colors(use_case: CatalogUseCase = Depends(get_color_use_case)):
    return await use_case.get_all()


@router.get("/colors/{id}", response_model=ColorResponse)
async def get_color(id: UUID, use_case: CatalogUseCase = Depends(get_color_use_case)):
    return await use_case.get_by_id(id)


@router.put(
    "/colors/{id}",
    response_model=ColorResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def update_color(
    id: UUID,
    data: BasicCatalogUpdate,
    use_case: CatalogUseCase = Depends(get_color_use_case),
):
    return await use_case.update(id, data)


# --- Sizes ---
@router.post(
    "/sizes",
    response_model=SizeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def create_size(
    data: BasicCatalogCreate, use_case: CatalogUseCase = Depends(get_size_use_case)
):
    return await use_case.create(data)


@router.get("/sizes", response_model=list[SizeResponse])
async def get_sizes(use_case: CatalogUseCase = Depends(get_size_use_case)):
    return await use_case.get_all()


@router.get("/sizes/{id}", response_model=SizeResponse)
async def get_size(id: UUID, use_case: CatalogUseCase = Depends(get_size_use_case)):
    return await use_case.get_by_id(id)


@router.put(
    "/sizes/{id}",
    response_model=SizeResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def update_size(
    id: UUID,
    data: BasicCatalogUpdate,
    use_case: CatalogUseCase = Depends(get_size_use_case),
):
    return await use_case.update(id, data)


# --- Categories ---
@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def create_category(
    data: BasicCatalogCreate, use_case: CatalogUseCase = Depends(get_category_use_case)
):
    return await use_case.create(data)


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(use_case: CatalogUseCase = Depends(get_category_use_case)):
    return await use_case.get_all()


@router.get("/categories/{id}", response_model=CategoryResponse)
async def get_category(
    id: UUID, use_case: CatalogUseCase = Depends(get_category_use_case)
):
    return await use_case.get_by_id(id)


@router.put(
    "/categories/{id}",
    response_model=CategoryResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def update_category(
    id: UUID,
    data: BasicCatalogUpdate,
    use_case: CatalogUseCase = Depends(get_category_use_case),
):
    return await use_case.update(id, data)


# --- Genders ---
@router.post(
    "/genders",
    response_model=GenderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def create_gender(
    data: BasicCatalogCreate, use_case: CatalogUseCase = Depends(get_gender_use_case)
):
    return await use_case.create(data)


@router.get("/genders", response_model=list[GenderResponse])
async def get_genders(use_case: CatalogUseCase = Depends(get_gender_use_case)):
    return await use_case.get_all()


@router.get("/genders/{id}", response_model=GenderResponse)
async def get_gender(id: UUID, use_case: CatalogUseCase = Depends(get_gender_use_case)):
    return await use_case.get_by_id(id)


@router.put(
    "/genders/{id}",
    response_model=GenderResponse,
    dependencies=[Depends(has_permission(Permission.MANAGE_CATALOG))],
)
async def update_gender(
    id: UUID,
    data: BasicCatalogUpdate,
    use_case: CatalogUseCase = Depends(get_gender_use_case),
):
    return await use_case.update(id, data)
