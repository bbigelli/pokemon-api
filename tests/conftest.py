import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pokemon_service import pokemon_service
from app.models.pokemon import PokemonResponse, PokemonSprites

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def mock_pokemon_data_dict():
    """Mock pokemon data dictionary fixture"""
    return {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [{"type": {"name": "electric"}}],
        "sprites": {
            "front_default": "https://example.com/front.png",
            "back_default": "https://example.com/back.png"
        }
    }

@pytest.fixture
def mock_pokemon_response():
    """Mock PokemonResponse object fixture"""
    return PokemonResponse(
        id=25,
        name="pikachu",
        height=4,
        weight=60,
        types=["electric"],
        sprites=PokemonSprites(
            front_default="https://example.com/front.png",
            back_default="https://example.com/back.png"
        )
    )

@pytest.fixture
def mock_pokemon_list_data():
    """Mock pokemon list data fixture"""
    return [
        {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "types": [{"type": {"name": "electric"}}],
            "sprites": {"front_default": None, "back_default": None}
        }
    ]

@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache before each test"""
    from app.core.cache import cache_service
    if cache_service.redis_client:
        cache_service.clear()
    yield

@pytest.fixture
def auth_headers(valid_api_key):
    """Authentication headers for protected endpoints"""
    return {"X-API-Key": valid_api_key}

@pytest.fixture
def valid_api_key():
    """Valid API key for testing"""
    return "dev-api-key-123"