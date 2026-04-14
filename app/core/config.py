from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    PROJECT_NAME: str = "Pokemon API"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pokemon_db"

    # Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600

    # Rate Limiting
    RATE_LIMIT: str = "100/minute"

    # PokeAPI
    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"
    POKEAPI_TIMEOUT: int = 30

    # Pagination
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 100

    # API Keys
    API_KEYS: str = "dev-api-key-123,test-api-key-456"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()


def get_api_keys() -> List[str]:
    """Parse API keys from string to list"""
    return [key.strip() for key in settings.API_KEYS.split(",") if key.strip()]
