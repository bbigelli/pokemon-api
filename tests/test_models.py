from app.models.pokemon import (
    PaginationMeta,
    PokemonListResponse,
    PokemonResponse,
    PokemonSprites,
)


def test_pokemon_sprites_model():
    """Test PokemonSprites model"""
    sprites = PokemonSprites(
        front_default="https://example.com/front.png",
        back_default="https://example.com/back.png",
    )

    assert sprites.front_default == "https://example.com/front.png"
    assert sprites.back_default == "https://example.com/back.png"


def test_pokemon_response_model():
    """Test PokemonResponse model"""
    pokemon = PokemonResponse(
        id=25,
        name="pikachu",
        height=4,
        weight=60,
        types=["electric"],
        sprites=PokemonSprites(front_default=None, back_default=None),
    )

    assert pokemon.id == 25
    assert pokemon.name == "pikachu"
    assert pokemon.height == 4
    assert pokemon.weight == 60
    assert len(pokemon.types) == 1


def test_pagination_meta_model():
    """Test PaginationMeta model"""
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


def test_pokemon_list_response_model():
    """Test PokemonListResponse model"""
    pokemon_list = PokemonListResponse(
        data=[],
        pagination=PaginationMeta(
            total=0, limit=20, offset=0, next=None, previous=None
        ),
    )

    assert pokemon_list.data == []
    assert pokemon_list.pagination.total == 0
