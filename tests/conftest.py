# Paso 19: tests/conftest.py
import os

# La configuración debe existir antes de importar la aplicación. Así los tests
# no dependen del archivo .env ni de secretos locales.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENVIRONMENT", "test")

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.database.models.base import Base
from src.interfaces.api.dependencies.database import get_db_session
from src.main import app

# Usar SQLite en memoria para pruebas
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)


@event.listens_for(engine.sync_engine, "connect")
def register_sqlite_functions(dbapi_connection, _connection_record) -> None:
    dbapi_connection.create_function("now", 0, lambda: datetime.now(UTC).isoformat())
    dbapi_connection.create_function("gen_random_uuid", 0, lambda: uuid4().hex)


TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
