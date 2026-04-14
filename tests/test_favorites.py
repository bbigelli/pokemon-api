import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import Session

client = TestClient(app)
VALID_API_KEY = "dev-api-key-123"
AUTH_HEADERS = {"X-API-Key": VALID_API_KEY}

# Setup test database
@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_favorite_success():
    """Test creating a favorite pokemon"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        response = client.post(
            "/api/v1/favorites",
            json={"pokemon_id": 25, "name": "pikachu", "nickname": "Pika", "notes": "My favorite"},
            headers=AUTH_HEADERS
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["pokemon_id"] == 25
        assert data["name"] == "pikachu"
        assert data["nickname"] == "Pika"

def test_create_favorite_already_exists():
    """Test creating a favorite that already exists"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        # Create first time
        client.post("/api/v1/favorites", json={"pokemon_id": 25, "name": "pikachu"}, headers=AUTH_HEADERS)
        
        # Create second time
        response = client.post(
            "/api/v1/favorites",
            json={"pokemon_id": 25, "name": "pikachu"},
            headers=AUTH_HEADERS
        )
        
        assert response.status_code == 409

def test_create_favorite_pokemon_not_found():
    """Test creating favorite with non-existent pokemon"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from fastapi import HTTPException
        mock_get.side_effect = HTTPException(status_code=404, detail="Pokemon not found")
        
        response = client.post(
            "/api/v1/favorites",
            json={"pokemon_id": 999999, "name": "unknown"},
            headers=AUTH_HEADERS
        )
        
        assert response.status_code == 404

def test_get_favorites_list():
    """Test getting list of favorites"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        # Create a favorite
        client.post("/api/v1/favorites", json={"pokemon_id": 25, "name": "pikachu"}, headers=AUTH_HEADERS)
        
        # Get list
        response = client.get("/api/v1/favorites", headers=AUTH_HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert len(data["data"]) > 0

def test_update_favorite():
    """Test updating a favorite"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        # Create
        create_response = client.post(
            "/api/v1/favorites",
            json={"pokemon_id": 25, "name": "pikachu", "nickname": "Pika"},
            headers=AUTH_HEADERS
        )
        favorite_id = create_response.json()["id"]
        
        # Update
        response = client.put(
            f"/api/v1/favorites/{favorite_id}",
            json={"nickname": "Pikachu Jr", "notes": "Updated notes"},
            headers=AUTH_HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "Pikachu Jr"
        assert data["notes"] == "Updated notes"

def test_delete_favorite():
    """Test deleting a favorite"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        # Create
        create_response = client.post(
            "/api/v1/favorites",
            json={"pokemon_id": 25, "name": "pikachu"},
            headers=AUTH_HEADERS
        )
        favorite_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/api/v1/favorites/{favorite_id}", headers=AUTH_HEADERS)
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/api/v1/favorites/{favorite_id}", headers=AUTH_HEADERS)
        assert get_response.status_code == 404

def test_get_favorite_by_pokemon_id():
    """Test getting favorite by pokemon_id"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id') as mock_get:
        from app.models.pokemon import PokemonResponse, PokemonSprites
        mock_get.return_value = PokemonResponse(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            types=["electric"],
            sprites=PokemonSprites(front_default=None, back_default=None)
        )
        
        # Create
        client.post("/api/v1/favorites", json={"pokemon_id": 25, "name": "pikachu"}, headers=AUTH_HEADERS)
        
        # Get by pokemon_id
        response = client.get("/api/v1/favorites/pokemon/25", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["pokemon_id"] == 25