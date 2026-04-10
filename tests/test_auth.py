import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from app.main import app
from app.core.auth import verify_api_key, optional_auth, VALID_API_KEYS, API_KEY_NAME
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_protected_endpoint_without_api_key():
    """Test protected endpoint without API key"""
    response = client.get("/api/v1/pokemons")
    assert response.status_code == 401
    assert "API key missing" in response.json()["detail"]

def test_protected_endpoint_with_invalid_api_key():
    """Test protected endpoint with invalid API key"""
    headers = {"X-API-Key": "invalid-key"}
    response = client.get("/api/v1/pokemons", headers=headers)
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]

def test_protected_endpoint_with_valid_api_key():
    """Test protected endpoint with valid API key"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_list') as mock_get_list:
        mock_get_list.return_value = ([], 0)
        
        headers = {"X-API-Key": VALID_API_KEYS[0]}
        response = client.get("/api/v1/pokemons?limit=1&offset=0", headers=headers)
        assert response.status_code == 200

def test_protected_detail_endpoint_with_valid_api_key():
    """Test protected detail endpoint with valid API key"""
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
        
        headers = {"X-API-Key": VALID_API_KEYS[0]}
        response = client.get("/api/v1/pokemons/25", headers=headers)
        assert response.status_code == 200

def test_public_endpoint_without_api_key():
    """Test public endpoint without API key (should work)"""
    with patch('app.services.pokemon_service.pokemon_service.get_pokemon_list') as mock_get_list:
        mock_get_list.return_value = ([], 0)
        
        response = client.get("/api/v1/public/pokemons?limit=1&offset=0")
        assert response.status_code == 200

def test_public_detail_endpoint_without_api_key():
    """Test public detail endpoint without API key (should work)"""
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
        
        response = client.get("/api/v1/public/pokemons/25")
        assert response.status_code == 200

def test_multiple_api_keys():
    """Test that multiple API keys work"""
    for api_key in VALID_API_KEYS:
        with patch('app.services.pokemon_service.pokemon_service.get_pokemon_list') as mock_get_list:
            mock_get_list.return_value = ([], 0)
            
            headers = {"X-API-Key": api_key}
            response = client.get("/api/v1/pokemons?limit=1&offset=0", headers=headers)
            assert response.status_code == 200

@pytest.mark.asyncio
async def test_verify_api_key_missing():
    """Test verify_api_key with missing key"""
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(None)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "API key missing" in exc_info.value.detail

@pytest.mark.asyncio
async def test_verify_api_key_invalid():
    """Test verify_api_key with invalid key"""
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key("invalid-key-123")
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Invalid API key" in exc_info.value.detail

@pytest.mark.asyncio
async def test_verify_api_key_valid():
    """Test verify_api_key with valid key"""
    result = await verify_api_key(VALID_API_KEYS[0])
    assert result == VALID_API_KEYS[0]

@pytest.mark.asyncio
async def test_optional_auth_with_valid_key():
    """Test optional_auth with valid API key"""
    result = await optional_auth(VALID_API_KEYS[0])
    assert result == VALID_API_KEYS[0]

@pytest.mark.asyncio
async def test_optional_auth_with_invalid_key():
    """Test optional_auth with invalid API key"""
    result = await optional_auth("invalid-key")
    assert result is None

@pytest.mark.asyncio
async def test_optional_auth_with_no_key():
    """Test optional_auth with no API key"""
    result = await optional_auth(None)
    assert result is None

def test_api_key_name_constant():
    """Test API_KEY_NAME constant"""
    assert API_KEY_NAME == "X-API-Key"

def test_valid_api_keys_list():
    """Test that VALID_API_KEYS is properly configured"""
    assert isinstance(VALID_API_KEYS, list)
    assert len(VALID_API_KEYS) > 0
    assert "dev-api-key-123" in VALID_API_KEYS