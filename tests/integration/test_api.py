# Paso 19: tests/integration/test_api.py
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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


# Aquí se agregarían más tests de integración:
# 1. Test para crear rol (bypassing auth or setting a mock token)
# 2. Test para crear usuario
# 3. Test de login exitoso
# 4. Test CRUD de inventario
# (En una aplicación real, usaríamos fixtures para inyectar datos semilla a la BD de pruebas)
