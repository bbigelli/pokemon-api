import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["version"] == "1.0.0"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_success(mock_get_list):
    """Test successful pokemon list retrieval"""
    mock_get_list.return_value = ([{
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [{"type": {"name": "electric"}}],
        "sprites": {"front_default": None, "back_default": None}
    }], 1281)
    
    response = client.get("/api/v1/pokemons?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 1
    assert data["pagination"]["offset"] == 0

def test_get_pokemons_invalid_limit():
    """Test invalid limit parameter"""
    response = client.get("/api/v1/pokemons?limit=200")
    assert response.status_code == 422  # Validation error

@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_by_id_success(mock_get_by_id, mock_pokemon_data):
    """Test successful pokemon retrieval by ID"""
    from tests.conftest import mock_pokemon_data
    mock_get_by_id.return_value = mock_pokemon_data
    
    response = client.get("/api/v1/pokemons/25")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 25
    assert data["name"] == "pikachu"

@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_get_pokemon_by_name_success(mock_get_by_name, mock_pokemon_data):
    """Test successful pokemon retrieval by name"""
    from tests.conftest import mock_pokemon_data
    mock_get_by_name.return_value = mock_pokemon_data
    
    response = client.get("/api/v1/pokemons/pikachu")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"

@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_not_found(mock_get_by_id):
    """Test pokemon not found"""
    from fastapi import HTTPException
    import httpx
    
    mock_get_by_id.side_effect = HTTPException(status_code=404, detail="Pokemon not found")
    
    response = client.get("/api/v1/pokemons/999999")
    assert response.status_code == 404