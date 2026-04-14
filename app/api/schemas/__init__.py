"""Pydantic schemas for request/response validation"""
from app.api.schemas.favorite import (
    FavoritePokemonBase,
    FavoritePokemonCreate,
    FavoritePokemonUpdate,
    FavoritePokemonResponse,
    FavoritePokemonListResponse,
)

__all__ = [
    "FavoritePokemonBase",
    "FavoritePokemonCreate",
    "FavoritePokemonUpdate",
    "FavoritePokemonResponse",
    "FavoritePokemonListResponse",
]
