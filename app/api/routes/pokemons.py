from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.services.pokemon_service import pokemon_service
from app.models.pokemon import PokemonResponse, PokemonListResponse, PaginationMeta
from app.core.config import settings
from app.core.rate_limit import limiter
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()

@router.get("/pokemons", response_model=PokemonListResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemons(
    request: Request,
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT),
    offset: int = Query(default=0, ge=0)
):
    """
    Get paginated list of pokemons
    
    - **limit**: Number of pokemons to return (1-100)
    - **offset**: Number of pokemons to skip
    """
    logger.info(f"Fetching pokemons - limit: {limit}, offset: {offset}")
    
    # Get data from service
    pokemons_data, total = await pokemon_service.get_pokemon_list(limit, offset)
    
    # Transform data
    pokemons = [pokemon_service._transform_pokemon_data(p) for p in pokemons_data]
    
    # Build pagination links
    next_offset = offset + limit
    previous_offset = offset - limit if offset - limit >= 0 else None
    
    next_url = f"/api/v1/pokemons?limit={limit}&offset={next_offset}" if next_offset < total else None
    previous_url = f"/api/v1/pokemons?limit={limit}&offset={previous_offset}" if previous_offset is not None else None
    
    return PokemonListResponse(
        data=pokemons,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            next=next_url,
            previous=previous_url
        )
    )

@router.get("/pokemons/{identifier}", response_model=PokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemon(
    request: Request,
    identifier: str
):
    """
    Get pokemon details by ID or name
    
    - **identifier**: Pokemon ID (number) or name (string)
    """
    logger.info(f"Fetching pokemon: {identifier}")
    
    # Check if identifier is numeric
    if identifier.isdigit():
        return await pokemon_service.get_pokemon_by_id(int(identifier))
    else:
        return await pokemon_service.get_pokemon_by_name(identifier)