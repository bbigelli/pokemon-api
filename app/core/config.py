from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    PROJECT_NAME: str = "Pokemon API"

    # Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour

    # Rate Limiting
    RATE_LIMIT: str = "100/minute"

    # PokeAPI
    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"
    POKEAPI_TIMEOUT: int = 30

    # Pagination
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 100

    # API Keys (comma-separated)
    API_KEYS: str = "dev-api-key-123,test-api-key-456"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env


settings = Settings()


# Parse API keys into a list
def get_api_keys() -> List[str]:
    """Parse API keys from string to list"""
    return [key.strip() for key in settings.API_KEYS.split(",") if key.strip()]
