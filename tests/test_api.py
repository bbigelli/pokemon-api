import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

client = TestClient(app)

# Valid API key for testing
VALID_API_KEY = "dev-api-key-123"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert data["message"] == "Welcome to Pokemon API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pokemon-api"


# Tests for protected endpoints (require API key)
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_success(mock_get_list, mock_pokemon_list_data):
    """Test successful pokemon list retrieval with API key"""
    mock_get_list.return_value = (mock_pokemon_list_data, 1281)

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?limit=1&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 1
    assert data["pagination"]["offset"] == 0
    assert data["pagination"]["total"] == 1281
    assert len(data["data"]) == 1


def test_get_pokemons_invalid_limit():
    """Test invalid limit parameter with API key"""
    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?limit=200", headers=headers)
    assert response.status_code == 422


def test_get_pokemons_invalid_offset():
    """Test invalid offset parameter with API key"""
    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?offset=-1", headers=headers)
    assert response.status_code == 422


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_default_values(mock_get_list):
    """Test default pagination values with API key"""
    mock_get_list.return_value = ([], 0)

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["limit"] == 20
    assert data["pagination"]["offset"] == 0


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_by_id_success(mock_get_by_id, mock_pokemon_response):
    """Test successful pokemon retrieval by ID with API key"""
    mock_get_by_id.return_value = mock_pokemon_response

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons/25", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 25
    assert data["name"] == "pikachu"
    assert data["height"] == 4
    assert data["weight"] == 60
    assert "electric" in data["types"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_get_pokemon_by_name_success(mock_get_by_name, mock_pokemon_response):
    """Test successful pokemon retrieval by name with API key"""
    mock_get_by_name.return_value = mock_pokemon_response

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons/pikachu", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    assert data["id"] == 25


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_not_found(mock_get_by_id):
    """Test pokemon not found with API key"""
    mock_get_by_id.side_effect = HTTPException(status_code=404, detail="Pokemon not found")

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons/999999", headers=headers)
    assert response.status_code == 404
    assert "Pokemon not found" in response.json().get("detail", "")


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_get_pokemon_by_name_not_found(mock_get_by_name):
    """Test pokemon not found by name with API key"""
    mock_get_by_name.side_effect = HTTPException(status_code=404, detail="Pokemon not found")

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons/unknownpokemon", headers=headers)
    assert response.status_code == 404


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_pagination_next_link(mock_get_list):
    """Test pagination next link generation with API key"""
    mock_get_list.return_value = ([], 100)

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?limit=20&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["next"] == "/api/v1/pokemons?limit=20&offset=20"
    assert data["pagination"]["previous"] is None


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_pagination_previous_link(mock_get_list):
    """Test pagination previous link generation with API key"""
    mock_get_list.return_value = ([], 100)

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?limit=20&offset=20", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["previous"] == "/api/v1/pokemons?limit=20&offset=0"


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_pagination_no_next_when_at_end(mock_get_list):
    """Test no next link when at end of list with API key"""
    mock_get_list.return_value = ([], 100)

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons?limit=20&offset=100", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["next"] is None


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_get_pokemon_with_invalid_id_format(mock_get_by_name):
    """Test getting pokemon with invalid ID format (should be treated as name and return 404)"""
    mock_get_by_name.side_effect = HTTPException(status_code=404, detail="Pokemon not found")

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.get("/api/v1/pokemons/25.5", headers=headers)
    assert response.status_code == 404


# Tests for public endpoints (no API key required)
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_get_pokemons_success(mock_get_list, mock_pokemon_list_data):
    """Test successful public pokemon list retrieval (no auth)"""
    mock_get_list.return_value = (mock_pokemon_list_data, 1281)

    response = client.get("/api/v1/public/pokemons?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 1
    assert data["pagination"]["offset"] == 0


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_public_get_pokemon_by_id_success(mock_get_by_id, mock_pokemon_response):
    """Test successful public pokemon retrieval by ID (no auth)"""
    mock_get_by_id.return_value = mock_pokemon_response

    response = client.get("/api/v1/public/pokemons/25")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 25
    assert data["name"] == "pikachu"


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_pagination_links(mock_get_list):
    """Test pagination links on public endpoint"""
    mock_get_list.return_value = ([], 100)

    response = client.get("/api/v1/public/pokemons?limit=20&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["next"] == "/api/v1/public/pokemons?limit=20&offset=20"
    assert data["pagination"]["previous"] is None


# Authentication tests
def test_protected_endpoint_without_api_key_returns_401():
    """Test protected endpoint without API key returns 401"""
    response = client.get("/api/v1/pokemons")
    assert response.status_code == 401
    assert "API key missing" in response.json()["detail"]


def test_protected_endpoint_with_invalid_api_key_returns_403():
    """Test protected endpoint with invalid API key returns 403"""
    headers = {"X-API-Key": "invalid-key"}
    response = client.get("/api/v1/pokemons", headers=headers)
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    headers = {"X-API-Key": VALID_API_KEY}

    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_list') as mock_get_list:
        mock_get_list.return_value = ([], 0)

        response = client.get("/api/v1/pokemons?limit=1&offset=0", headers=headers)
        assert response.status_code == 200
        assert response.headers.get("x-process-time") is not None


# Unexpected error tests for protected endpoints
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_unexpected_error(mock_get_by_id, auth_headers):
    """Test unexpected error handling in pokemon endpoint"""
    mock_get_by_id.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/pokemons/25", headers=auth_headers)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_unexpected_error(mock_get_list, auth_headers):
    """Test unexpected error in get_pokemons endpoint"""
    mock_get_list.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/pokemons?limit=20&offset=0", headers=auth_headers)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_by_id_unexpected_error(mock_get_by_id, auth_headers):
    """Test unexpected error in get_pokemon_by_id endpoint"""
    mock_get_by_id.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/pokemons/25", headers=auth_headers)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


# Unexpected error tests for public endpoints
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_public_get_pokemon_unexpected_error(mock_get_by_name):
    """Test unexpected error handling in public pokemon endpoint"""
    mock_get_by_name.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/public/pokemons/pikachu")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_get_pokemons_unexpected_error(mock_get_list):
    """Test unexpected error in public get_pokemons endpoint"""
    mock_get_list.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/public/pokemons?limit=20&offset=0")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_public_get_pokemon_by_name_unexpected_error(mock_get_by_name):
    """Test unexpected error in public get_pokemon_by_name endpoint"""
    mock_get_by_name.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/public/pokemons/pikachu")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_public_get_pokemon_by_id_unexpected_error(mock_get_by_id):
    """Test unexpected error in public get pokemon by id endpoint"""
    mock_get_by_id.side_effect = Exception("Unexpected database error")

    response = client.get("/api/v1/public/pokemons/25")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_get_pokemons_specific_unexpected_error(mock_get_list):
    """Test specific unexpected error in public get pokemons endpoint"""
    mock_get_list.side_effect = ConnectionError("Connection failed")

    response = client.get("/api/v1/public/pokemons?limit=20&offset=0")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


# HTTP exception propagation tests
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_http_exception_propagation(mock_get_list, auth_headers):
    """Test HTTP exception propagation in get_pokemons"""
    mock_get_list.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")

    response = client.get("/api/v1/pokemons?limit=20&offset=0", headers=auth_headers)
    assert response.status_code == 429


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_get_pokemon_http_exception_propagation(mock_get_by_id, auth_headers):
    """Test HTTP exception propagation in get_pokemon"""
    mock_get_by_id.side_effect = HTTPException(status_code=404, detail="Not found")

    response = client.get("/api/v1/pokemons/25", headers=auth_headers)
    assert response.status_code == 404


# Additional coverage tests
def test_get_pokemons_with_max_limit():
    """Test get pokemons with max limit"""
    headers = {"X-API-Key": VALID_API_KEY}

    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_list') as mock_get_list:
        mock_get_list.return_value = ([], 0)

        response = client.get("/api/v1/pokemons?limit=100", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["limit"] == 100


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_get_pokemon_by_name_with_uppercase(mock_get_by_name, mock_pokemon_response, auth_headers):
    """Test get pokemon by name with uppercase letters"""
    mock_get_by_name.return_value = mock_pokemon_response

    response = client.get("/api/v1/pokemons/PIKACHU", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    mock_get_by_name.assert_called_once_with("pikachu")


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_public_get_pokemon_by_name_with_uppercase(mock_get_by_name, mock_pokemon_response):
    """Test public get pokemon by name with uppercase letters"""
    mock_get_by_name.return_value = mock_pokemon_response

    response = client.get("/api/v1/public/pokemons/PIKACHU")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    mock_get_by_name.assert_called_once_with("pikachu")


# Specific tests to cover lines 110 and 133 (except Exception blocks)
@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_name')
def test_public_get_pokemon_covers_line_110_exception(mock_get_by_name):
    """Test to cover line 110 - except Exception in get_pokemon_public with name"""
    mock_get_by_name.side_effect = RuntimeError("Runtime error to cover line 110")

    response = client.get("/api/v1/public/pokemons/pikachu")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_by_id')
def test_public_get_pokemon_by_id_covers_line_110_exception(mock_get_by_id):
    """Test to cover line 110 - except Exception in get_pokemon_public with ID"""
    mock_get_by_id.side_effect = RuntimeError("Runtime error to cover line 110")

    response = client.get("/api/v1/public/pokemons/25")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_get_pokemons_covers_line_133_exception(mock_get_list):
    """Test to cover line 133 - except Exception in get_pokemons_public"""
    mock_get_list.side_effect = RuntimeError("Runtime error to cover line 133")

    response = client.get("/api/v1/public/pokemons?limit=20&offset=0")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_public_get_pokemons_with_value_error_covers_line_133(mock_get_list):
    """Test to cover line 133 with ValueError"""
    mock_get_list.side_effect = ValueError("Value error to cover line 133")

    response = client.get("/api/v1/public/pokemons?limit=20&offset=0")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@patch('app.services.pokemon_service.pokemon_service.get_pokemon_list')
def test_get_pokemons_unexpected_error_with_connection_error(mock_get_list, auth_headers):
    """Test unexpected error with ConnectionError in get_pokemons"""
    mock_get_list.side_effect = ConnectionError("Connection failed")

    response = client.get("/api/v1/pokemons?limit=20&offset=0", headers=auth_headers)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]