import pytest

from app.models.pokemon import PaginationMeta


def test_pagination_metadata():
    """Test pagination metadata creation"""
    pagination = PaginationMeta(
        total=100,
        limit=20,
        offset=0,
        next="/pokemons?limit=20&offset=20",
        previous=None,
    )

    assert pagination.total == 100
    assert pagination.limit == 20
    assert pagination.offset == 0
    assert pagination.next == "/pokemons?limit=20&offset=20"
    assert pagination.previous is None


def test_pagination_with_previous():
    """Test pagination with previous link"""
    pagination = PaginationMeta(
        total=100,
        limit=20,
        offset=20,
        next="/pokemons?limit=20&offset=40",
        previous="/pokemons?limit=20&offset=0",
    )

    assert pagination.previous is not None
