import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
import httpx
from app.services.pokemon_service import pokemon_service, PokemonService
from app.models.pokemon import PokemonResponse, PokemonSprites


@pytest.mark.asyncio
async def test_make_request_success():
    """Test successful request to PokeAPI"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "pikachu"}
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await pokemon_service._make_request(
            "https://pokeapi.co/api/v2/pokemon/25"
        )
        assert result == {"name": "pikachu"}


@pytest.mark.asyncio
async def test_make_request_timeout():
    """Test request timeout handling"""
    service = PokemonService()

    with patch("httpx.AsyncClient") as mock_client:
        # Simulate timeout exception usando o tipo correto
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.ConnectTimeout("Connection timeout")
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("https://pokeapi.co/api/v2/pokemon/25")

        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_make_request_404():
    """Test 404 error handling"""
    service = PokemonService()

    with patch("httpx.AsyncClient") as mock_client:
        # Create a proper HTTPStatusError for 404
        mock_response = MagicMock()
        mock_response.status_code = 404

        error = httpx.HTTPStatusError(
            "404 Error", request=MagicMock(), response=mock_response
        )

        mock_response.raise_for_status = MagicMock(side_effect=error)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("https://pokeapi.co/api/v2/pokemon/999999")

        assert exc_info.value.status_code == 404
        assert "Pokemon not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_make_request_500():
    """Test 500 error handling from PokeAPI"""
    service = PokemonService()

    with patch("httpx.AsyncClient") as mock_client:
        # Create a proper HTTPStatusError for 500
        mock_response = MagicMock()
        mock_response.status_code = 500

        error = httpx.HTTPStatusError(
            "500 Error", request=MagicMock(), response=mock_response
        )

        mock_response.raise_for_status = MagicMock(side_effect=error)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("https://pokeapi.co/api/v2/pokemon/25")

        assert exc_info.value.status_code == 502
        assert "PokeAPI error" in exc_info.value.detail


@pytest.mark.asyncio
async def test_make_request_general_exception():
    """Test general exception handling"""
    service = PokemonService()

    with patch("httpx.AsyncClient") as mock_client:
        # Simulate general exception
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=RuntimeError("Something went wrong")
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._make_request("https://pokeapi.co/api/v2/pokemon/25")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail


@pytest.mark.asyncio
async def test_make_request_with_cache():
    """Test that cache is used for subsequent requests"""
    service = PokemonService()

    with patch("httpx.AsyncClient") as mock_client, patch(
        "app.services.pokemon_service.cache_service"
    ) as mock_cache:
        # Mock cache miss then hit
        mock_cache.get.side_effect = [None, {"name": "pikachu"}]
        mock_cache.set.return_value = True

        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "pikachu"}
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        # First request - should hit the API
        result1 = await service._make_request("https://pokeapi.co/api/v2/pokemon/25")
        assert result1 == {"name": "pikachu"}

        # Second request - should use cache
        result2 = await service._make_request("https://pokeapi.co/api/v2/pokemon/25")
        assert result2 == {"name": "pikachu"}


@pytest.mark.asyncio
async def test_transform_pokemon_data():
    """Test data transformation"""
    raw_data = {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [{"type": {"name": "electric"}}, {"type": {"name": "flying"}}],
        "sprites": {
            "front_default": "https://example.com/front.png",
            "back_default": "https://example.com/back.png",
        },
    }

    result = pokemon_service._transform_pokemon_data(raw_data)

    assert isinstance(result, PokemonResponse)
    assert result.id == 25
    assert result.name == "pikachu"
    assert result.height == 4
    assert result.weight == 60
    assert len(result.types) == 2
    assert "electric" in result.types
    assert "flying" in result.types
    assert result.sprites.front_default == "https://example.com/front.png"


@pytest.mark.asyncio
async def test_get_pokemon_by_id():
    """Test get pokemon by ID"""
    with patch.object(
        pokemon_service, "_make_request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "types": [{"type": {"name": "electric"}}],
            "sprites": {"front_default": None, "back_default": None},
        }

        result = await pokemon_service.get_pokemon_by_id(25)

        assert result.id == 25
        assert result.name == "pikachu"
        mock_request.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/25")


@pytest.mark.asyncio
async def test_get_pokemon_by_name():
    """Test get pokemon by name"""
    with patch.object(
        pokemon_service, "_make_request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "types": [{"type": {"name": "electric"}}],
            "sprites": {"front_default": None, "back_default": None},
        }

        result = await pokemon_service.get_pokemon_by_name("pikachu")

        assert result.name == "pikachu"
        mock_request.assert_called_once_with(
            "https://pokeapi.co/api/v2/pokemon/pikachu"
        )


@pytest.mark.asyncio
async def test_get_pokemon_list():
    """Test get pokemon list"""
    with patch.object(
        pokemon_service, "_make_request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = [
            {
                "count": 1281,
                "results": [
                    {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon/25/"}
                ],
            },
            {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "types": [{"type": {"name": "electric"}}],
                "sprites": {"front_default": None, "back_default": None},
            },
        ]

        result, total = await pokemon_service.get_pokemon_list(1, 0)

        assert len(result) == 1
        assert total == 1281
        assert result[0]["name"] == "pikachu"
