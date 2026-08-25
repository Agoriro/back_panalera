# Paso 19: tests/integration/test_api.py
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.catalog import (
    CategoryModel,
    ColorModel,
    GenderModel,
    SizeModel,
    SupplierModel,
)
from src.infrastructure.database.models.inventory import (
    InventoryModel,
    InventoryPhotoModel,
)
from src.infrastructure.database.models.role import RoleModel
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.security.jwt import create_access_token, create_refresh_token
from src.infrastructure.security.password import get_password_hash


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_login_failed_wrong_credentials(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"}
    )
    # As the DB is empty in test, the user doesn't exist yet, so it should return 401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_endpoint_rejects_access_token(async_client: AsyncClient):
    access_token = create_access_token({"sub": "8507f5cb-ea80-4bd3-af28-1f2cfbbccc7e"})

    response = await async_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": access_token}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_refresh_token(async_client: AsyncClient):
    refresh_token = create_refresh_token(
        {"sub": "8507f5cb-ea80-4bd3-af28-1f2cfbbccc7e", "ver": 0}
    )

    response = await async_client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_refresh_rotation_and_disabled_user(
    async_client: AsyncClient, db_session: AsyncSession
):
    role = RoleModel(id_role=uuid4(), name="Admin")
    user = UserModel(
        id_user=uuid4(),
        user="secure-admin",
        password=get_password_hash("secure-password"),
        id_role=role.id_role,
        is_active=True,
        token_version=0,
    )
    db_session.add_all([role, user])
    await db_session.commit()

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "secure-admin", "password": "secure-password"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["refresh_token"] != tokens["refresh_token"]

    reused_response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused_response.status_code == 401

    user.is_active = False
    await db_session.commit()
    protected_response = await async_client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert protected_response.status_code == 401


@pytest.mark.asyncio
async def test_endpoint_role_matrix(
    async_client: AsyncClient, db_session: AsyncSession
):
    admin_role = RoleModel(id_role=uuid4(), name="Admin")
    operator_role = RoleModel(id_role=uuid4(), name="Operator")
    read_role = RoleModel(id_role=uuid4(), name="Consulta")
    admin = UserModel(
        id_user=uuid4(),
        user="matrix-admin",
        password="unused",
        id_role=admin_role.id_role,
        is_active=True,
    )
    operator = UserModel(
        id_user=uuid4(),
        user="matrix-operator",
        password="unused",
        id_role=operator_role.id_role,
        is_active=True,
    )
    reader = UserModel(
        id_user=uuid4(),
        user="matrix-reader",
        password="unused",
        id_role=read_role.id_role,
        is_active=True,
    )
    db_session.add_all([admin_role, operator_role, read_role, admin, operator, reader])
    admin_id = admin.id_user
    operator_id = operator.id_user
    reader_id = reader.id_user
    await db_session.commit()

    def headers_for(user_id: UUID) -> dict[str, str]:
        token = create_access_token({"sub": str(user_id)})
        return {"Authorization": f"Bearer {token}"}

    no_token_response = await async_client.get("/api/v1/inventory")
    assert no_token_response.status_code == 401

    admin_response = await async_client.get(
        "/api/v1/users", headers=headers_for(admin_id)
    )
    assert admin_response.status_code == 200

    operator_read = await async_client.get(
        "/api/v1/catalog/colors", headers=headers_for(operator_id)
    )
    assert operator_read.status_code == 200
    operator_catalog_write = await async_client.post(
        "/api/v1/catalog/colors",
        json={"name": "Azul"},
        headers=headers_for(operator_id),
    )
    assert operator_catalog_write.status_code == 403
    operator_inventory_write = await async_client.post(
        "/api/v1/inventory", json={}, headers=headers_for(operator_id)
    )
    assert operator_inventory_write.status_code == 422

    reader_write = await async_client.post(
        "/api/v1/movements/sale",
        json={"id_inventory": str(uuid4()), "quantity": 1},
        headers=headers_for(reader_id),
    )
    assert reader_write.status_code == 403
    reader_read = await async_client.get(
        "/api/v1/movements", headers=headers_for(reader_id)
    )
    assert reader_read.status_code == 200


@pytest.mark.asyncio
async def test_stock_never_becomes_negative(
    async_client: AsyncClient, db_session: AsyncSession
):
    role = RoleModel(id_role=uuid4(), name="Operator")
    user = UserModel(
        id_user=uuid4(),
        user="stock-operator",
        password="unused",
        id_role=role.id_role,
        is_active=True,
    )
    supplier = SupplierModel(
        id_supplier=uuid4(), name_supplier="Proveedor", is_active=True
    )
    color = ColorModel(id_color=uuid4(), name_color="Azul")
    size = SizeModel(id_size=uuid4(), name_size="M")
    category = CategoryModel(id_category=uuid4(), name_category="Pañales")
    gender = GenderModel(id_gender=uuid4(), name_gender="Unisex")
    inventory = InventoryModel(
        id_inventory=uuid4(),
        description_inventory="Producto",
        utility=Decimal("0.25"),
        id_supplier=supplier.id_supplier,
        id_color=color.id_color,
        id_size=size.id_size,
        id_category=category.id_category,
        id_gender=gender.id_gender,
        is_active=True,
    )
    db_session.add_all([role, user, supplier, color, size, category, gender, inventory])
    user_id = user.id_user
    supplier_id = supplier.id_supplier
    inventory_id = inventory.id_inventory
    await db_session.commit()
    headers = {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}

    purchase = await async_client.post(
        "/api/v1/movements/purchase",
        json={
            "id_supplier": str(supplier_id),
            "id_inventory": str(inventory_id),
            "quantity": 3,
            "value": "100.00",
        },
        headers=headers,
    )
    assert purchase.status_code == 201

    excessive_sale = await async_client.post(
        "/api/v1/movements/sale",
        json={"id_inventory": str(inventory_id), "quantity": 4},
        headers=headers,
    )
    assert excessive_sale.status_code == 422

    exact_sale = await async_client.post(
        "/api/v1/movements/sale",
        json={"id_inventory": str(inventory_id), "quantity": 3},
        headers=headers,
    )
    assert exact_sale.status_code == 201

    extra_sale = await async_client.post(
        "/api/v1/movements/sale",
        json={"id_inventory": str(inventory_id), "quantity": 1},
        headers=headers,
    )
    assert extra_sale.status_code == 422

    movements = await async_client.get(
        f"/api/v1/movements?id_inventory={inventory_id}", headers=headers
    )
    assert movements.status_code == 200
    assert [item["type_movement"] for item in movements.json()] == ["Sell", "Buy"]


@pytest.mark.asyncio
async def test_inventory_integrity_rules(
    async_client: AsyncClient, db_session: AsyncSession
):
    role = RoleModel(id_role=uuid4(), name="Admin")
    user = UserModel(
        id_user=uuid4(),
        user="inventory-admin",
        password="unused",
        id_role=role.id_role,
        is_active=True,
    )
    supplier = SupplierModel(
        id_supplier=uuid4(), name_supplier="Proveedor integridad", is_active=True
    )
    color = ColorModel(id_color=uuid4(), name_color="Verde")
    size = SizeModel(id_size=uuid4(), name_size="L")
    category = CategoryModel(id_category=uuid4(), name_category="Accesorios")
    gender = GenderModel(id_gender=uuid4(), name_gender="Universal")
    first_inventory = InventoryModel(
        id_inventory=uuid4(),
        description_inventory="Artículo uno",
        code_inventory="SKU-UNICO",
        barcode_inventory="BARCODE-UNICO",
        utility=Decimal("0.20"),
        id_supplier=supplier.id_supplier,
        id_color=color.id_color,
        id_size=size.id_size,
        id_category=category.id_category,
        id_gender=gender.id_gender,
        is_active=True,
    )
    second_inventory = InventoryModel(
        id_inventory=uuid4(),
        description_inventory="Artículo dos",
        utility=Decimal("0.20"),
        id_supplier=supplier.id_supplier,
        id_color=color.id_color,
        id_size=size.id_size,
        id_category=category.id_category,
        id_gender=gender.id_gender,
        is_active=True,
    )
    photo = InventoryPhotoModel(
        id_reg=uuid4(),
        id_inventory=first_inventory.id_inventory,
        url_photo="https://example.com/photo.jpg",
    )
    db_session.add_all(
        [
            role,
            user,
            supplier,
            color,
            size,
            category,
            gender,
            first_inventory,
            second_inventory,
            photo,
        ]
    )
    user_id = user.id_user
    supplier_id = supplier.id_supplier
    color_id = color.id_color
    size_id = size.id_size
    category_id = category.id_category
    gender_id = gender.id_gender
    first_inventory_id = first_inventory.id_inventory
    second_inventory_id = second_inventory.id_inventory
    photo_id = photo.id_reg
    await db_session.commit()
    headers = {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}
    base_payload = {
        "description_inventory": "Nuevo artículo",
        "utility": "0.20",
        "id_supplier": str(supplier_id),
        "id_color": str(color_id),
        "id_size": str(size_id),
        "id_category": str(category_id),
        "id_gender": str(gender_id),
    }

    duplicate_sku = await async_client.post(
        "/api/v1/inventory",
        json={**base_payload, "code_inventory": "SKU-UNICO"},
        headers=headers,
    )
    assert duplicate_sku.status_code == 409
    assert duplicate_sku.json()["detail"] == "El SKU ya existe"

    duplicate_barcode = await async_client.post(
        "/api/v1/inventory",
        json={**base_payload, "barcode_inventory": "BARCODE-UNICO"},
        headers=headers,
    )
    assert duplicate_barcode.status_code == 409
    assert duplicate_barcode.json()["detail"] == "El código de barras ya existe"

    invalid_relation = await async_client.put(
        f"/api/v1/inventory/{second_inventory_id}",
        json={"id_category": str(uuid4())},
        headers=headers,
    )
    assert invalid_relation.status_code == 404
    assert invalid_relation.json()["detail"] == "Category no encontrado"

    cross_inventory_delete = await async_client.delete(
        f"/api/v1/inventory/{second_inventory_id}/photos/{photo_id}",
        headers=headers,
    )
    assert cross_inventory_delete.status_code == 404
    persisted_photo = await db_session.scalar(
        select(InventoryPhotoModel).where(InventoryPhotoModel.id_reg == photo_id)
    )
    assert persisted_photo is not None

    invalid_photo_url = await async_client.post(
        f"/api/v1/inventory/{second_inventory_id}/photos",
        json={"url_photos": ["not-a-url"]},
        headers=headers,
    )
    assert invalid_photo_url.status_code == 422

    too_many_photos = await async_client.post(
        f"/api/v1/inventory/{first_inventory_id}/photos",
        json={
            "url_photos": [
                f"https://example.com/photo-{index}.jpg" for index in range(10)
            ]
        },
        headers=headers,
    )
    assert too_many_photos.status_code == 422
    assert too_many_photos.json()["detail"] == "Máximo 10 fotos por artículo"

    normalized = await async_client.put(
        f"/api/v1/inventory/{second_inventory_id}",
        json={"code_inventory": "   ", "barcode_inventory": ""},
        headers=headers,
    )
    assert normalized.status_code == 200
    assert normalized.json()["code_inventory"] is None
    assert normalized.json()["barcode_inventory"] is None


# Aquí se agregarían más tests de integración:
# 1. Test para crear rol (bypassing auth or setting a mock token)
# 2. Test para crear usuario
# 3. Test de login exitoso
# 4. Test CRUD de inventario
# (En una aplicación real, usaríamos fixtures para inyectar datos semilla a la BD de pruebas)
