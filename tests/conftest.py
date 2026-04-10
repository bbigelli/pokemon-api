import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pokemon_service import pokemon_service

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def mock_pokemon_data():
    """Mock pokemon data fixture"""
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