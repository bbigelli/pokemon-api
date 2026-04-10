import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_exception_in_public_pokemon_by_name():
    """Force exception in get_pokemon_public by name - should execute line 113"""
    with patch(
        "app.services.pokemon_service.pokemon_service.get_pokemon_by_name"
    ) as mock:
        # Force ANY exception to trigger the except block
        mock.side_effect = Exception("Forced exception for testing")

        response = client.get("/api/v1/public/pokemons/pikachu")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]


def test_exception_in_public_pokemon_by_id():
    """Force exception in get_pokemon_public by id - should execute line 113"""
    with patch(
        "app.services.pokemon_service.pokemon_service.get_pokemon_by_id"
    ) as mock:
        # Force ANY exception to trigger the except block
        mock.side_effect = Exception("Forced exception for testing")

        response = client.get("/api/v1/public/pokemons/25")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]


def test_exception_in_public_pokemons_list():
    """Force exception in get_pokemons_public - should execute line 138"""
    with patch("app.services.pokemon_service.pokemon_service.get_pokemon_list") as mock:
        # Force ANY exception to trigger the except block
        mock.side_effect = Exception("Forced exception for testing")

        response = client.get("/api/v1/public/pokemons?limit=20&offset=0")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]


def test_runtime_error_in_public_pokemons_list():
    """Force RuntimeError in get_pokemons_public - should execute line 138"""
    with patch("app.services.pokemon_service.pokemon_service.get_pokemon_list") as mock:
        # Force RuntimeError
        mock.side_effect = RuntimeError("Runtime error for testing")

        response = client.get("/api/v1/public/pokemons?limit=20&offset=0")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]


def test_value_error_in_public_pokemons_list():
    """Force ValueError in get_pokemons_public - should execute line 138"""
    with patch("app.services.pokemon_service.pokemon_service.get_pokemon_list") as mock:
        # Force ValueError
        mock.side_effect = ValueError("Value error for testing")

        response = client.get("/api/v1/public/pokemons?limit=20&offset=0")

        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
