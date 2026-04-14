from app.core.config import settings, get_api_keys


def test_config_default_values():
    """Test default configuration values"""
    # DEBUG pode ser True em ambiente de teste, então verificamos apenas o tipo
    assert isinstance(settings.DEBUG, bool)
    assert settings.DEFAULT_LIMIT == 20
    assert settings.MAX_LIMIT == 100
    assert settings.CACHE_TTL == 3600
    assert settings.RATE_LIMIT == "100/minute"
    assert settings.POKEAPI_BASE_URL == "https://pokeapi.co/api/v2"
    assert settings.POKEAPI_TIMEOUT == 30
    assert settings.API_KEYS is not None


def test_get_api_keys():
    """Test API keys parsing"""
    keys = get_api_keys()
    assert isinstance(keys, list)
    assert len(keys) > 0
    assert "dev-api-key-123" in keys
