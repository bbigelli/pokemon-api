import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pokemon_service import pokemon_service
from app.models.pokemon import PokemonResponse, PokemonSprites
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import Session
from app.core.config import settings
import os

# Configurar banco de dados de teste
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def client():
    """Test client fixture"""
    # Recriar tabelas para cada teste
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    from app.core.database import SessionLocal
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()

@pytest.fixture
def db_session():
    """Database session fixture for testing"""
    Base.metadata.create_all(bind=engine)
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

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

@pytest.fixture
def valid_api_key():
    """Valid API key for testing"""
    return "dev-api-key-123"

@pytest.fixture
def auth_headers(valid_api_key):
    """Authentication headers for protected endpoints"""
    return {"X-API-Key": valid_api_key}