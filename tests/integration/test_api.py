# Paso 19: tests/integration/test_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_login_failed_wrong_credentials(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    # As the DB is empty in test, the user doesn't exist yet, so it should return 401
    assert response.status_code == 401

# Aquí se agregarían más tests de integración:
# 1. Test para crear rol (bypassing auth or setting a mock token)
# 2. Test para crear usuario
# 3. Test de login exitoso
# 4. Test CRUD de inventario
# (En una aplicación real, usaríamos fixtures para inyectar datos semilla a la BD de pruebas)
