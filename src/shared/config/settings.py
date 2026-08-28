# Paso 5: src/shared/config/settings.py
"""
Módulo de configuración de la aplicación usando Pydantic Settings.
Carga variables de entorno y proporciona valores predeterminados.
"""

from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Clase de configuración principal.
    Las variables de entorno sobrescriben estos valores.
    """

    # Entorno
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Base de Datos
    DATABASE_URL: str
    DB_POOL_SIZE: int = Field(5, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(10, ge=0, le=100)
    DB_POOL_TIMEOUT_SECONDS: int = Field(10, ge=1, le=120)
    DB_POOL_RECYCLE_SECONDS: int = Field(1800, ge=60)
    DB_COMMAND_TIMEOUT_SECONDS: int = Field(30, ge=1, le=300)
    DB_HEALTH_TIMEOUT_SECONDS: int = Field(3, ge=1, le=30)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            # Render y otros proveedores usan postgres:// o postgresql://
            # asyncpg requiere el esquema postgresql+asyncpg://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith(
                "postgresql+asyncpg://"
            ):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Bootstrap opcional. Nunca hay credenciales predeterminadas.
    BOOTSTRAP_ADMIN_USERNAME: str | None = None
    BOOTSTRAP_ADMIN_PASSWORD: SecretStr | None = None

    # CORS (separados por coma si son múltiples)
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,https://front-panalera.vercel.app"
    )

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_allowed_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins or "*" in origins:
            raise ValueError(
                "ALLOWED_ORIGINS debe contener orígenes explícitos; '*' no está permitido"
            )
        for origin in origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
                or parsed.path not in {"", "/"}
            ):
                raise ValueError(f"Origen CORS inválido: {origin}")
        return ",".join(origin.rstrip("/") for origin in origins)

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        origins = self.cors_origins_list
        if self.ENVIRONMENT.lower() == "production":
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY debe tener al menos 32 caracteres en producción"
                )
            if any(not origin.startswith("https://") for origin in origins):
                raise ValueError("ALLOWED_ORIGINS solo admite HTTPS en producción")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        """Devuelve la lista de orígenes permitidos separados por coma."""
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Instancia global de settings
settings = Settings()
