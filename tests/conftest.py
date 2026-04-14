import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pokemon_service import pokemon_service
from app.models.pokemon import PokemonResponse, PokemonSprites
from app.core.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Configurar banco de dados de teste (SQLite em memória)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Criar engine de teste
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Criar sessão de teste
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Aplicar override da dependência
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database - cria tabelas antes dos testes"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Database session fixture for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
            "back_default": "https://example.com/back.png",
        },
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
            back_default="https://example.com/back.png",
        ),
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
            "sprites": {"front_default": None, "back_default": None},
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
