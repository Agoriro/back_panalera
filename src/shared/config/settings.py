# Paso 5: src/shared/config/settings.py
"""
Módulo de configuración de la aplicación usando Pydantic Settings.
Carga variables de entorno y proporciona valores predeterminados.
"""

from typing import List
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

    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Devuelve la lista de orígenes permitidos separados por coma."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia global de settings
settings = Settings()
