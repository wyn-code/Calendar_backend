from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación, cargada desde variables de entorno y `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- General ---
    PROJECT_NAME: str = "Agenda Psicologa API"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Base de datos ---
    DATABASE_URL: str

    # --- Seguridad / JWT ---
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- CORS (orígenes permitidos para el frontend React) ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "calendar-proyect-one.vercel.app",
    ]


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia única (caché) de la configuración."""
    return Settings()


settings = get_settings()
