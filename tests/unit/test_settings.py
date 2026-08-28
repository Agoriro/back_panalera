import pytest
from pydantic import ValidationError

from src.shared.config.settings import Settings


def production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "DATABASE_URL": "postgresql+asyncpg://user:password@db/database",
        "SECRET_KEY": "x" * 32,
        "ENVIRONMENT": "production",
        "ALLOWED_ORIGINS": "https://app.example.com",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="orígenes explícitos"):
        production_settings(ALLOWED_ORIGINS="*")


def test_production_requires_https_origins() -> None:
    with pytest.raises(ValidationError, match="solo admite HTTPS"):
        production_settings(ALLOWED_ORIGINS="http://app.example.com")


def test_production_accepts_explicit_https_origins() -> None:
    configured = production_settings(
        ALLOWED_ORIGINS="https://app.example.com, https://admin.example.com"
    )

    assert configured.cors_origins_list == [
        "https://app.example.com",
        "https://admin.example.com",
    ]
