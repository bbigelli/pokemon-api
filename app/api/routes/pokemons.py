from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from typing import Optional
from app.services.pokemon_service import pokemon_service
from app.models.pokemon import PokemonResponse, PokemonListResponse, PaginationMeta
from app.core.config import settings
from app.core.rate_limit import limiter
from app.utils.logger import setup_logger
from app.core.auth import verify_api_key

router = APIRouter()
logger = setup_logger()


# Protected endpoints (require API key)
@router.get("/pokemons", response_model=PokemonListResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemons(
    request: Request,
    api_key: str = Depends(verify_api_key),
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    """Get paginated list of pokemons (requires API key)"""
    logger.info(f"Fetching pokemons - limit: {limit}, offset: {offset}")

    try:
        pokemons_data, total = await pokemon_service.get_pokemon_list(limit, offset)
        pokemons = [pokemon_service._transform_pokemon_data(p) for p in pokemons_data]

        next_offset = offset + limit
        previous_offset = offset - limit if offset - limit >= 0 else None

        next_url = (
            f"/api/v1/pokemons?limit={limit}&offset={next_offset}"
            if next_offset < total
            else None
        )
        previous_url = (
            f"/api/v1/pokemons?limit={limit}&offset={previous_offset}"
            if previous_offset is not None
            else None
        )

        return PokemonListResponse(
            data=pokemons,
            pagination=PaginationMeta(
                total=total,
                limit=limit,
                offset=offset,
                next=next_url,
                previous=previous_url,
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pokemons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/pokemons/{identifier}", response_model=PokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemon(
    request: Request, identifier: str, api_key: str = Depends(verify_api_key)
):
    """Get pokemon details by ID or name (requires API key)"""
    logger.info(f"Fetching pokemon: {identifier}")

    try:
        if identifier.isdigit():
            return await pokemon_service.get_pokemon_by_id(int(identifier))
        else:
            return await pokemon_service.get_pokemon_by_name(identifier.lower())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pokemon: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Public endpoints (no auth required)
@router.get("/public/pokemons", response_model=PokemonListResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemons_public(
    request: Request,
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    """Get paginated list of pokemons (public endpoint)"""
    logger.info(f"Fetching pokemons (public) - limit: {limit}, offset: {offset}")

    try:
        pokemons_data, total = await pokemon_service.get_pokemon_list(limit, offset)
        pokemons = [pokemon_service._transform_pokemon_data(p) for p in pokemons_data]

        next_offset = offset + limit
        previous_offset = offset - limit if offset - limit >= 0 else None

        next_url = (
            f"/api/v1/public/pokemons?limit={limit}&offset={next_offset}"
            if next_offset < total
            else None
        )
        previous_url = (
            f"/api/v1/public/pokemons?limit={limit}&offset={previous_offset}"
            if previous_offset is not None
            else None
        )

        return PokemonListResponse(
            data=pokemons,
            pagination=PaginationMeta(
                total=total,
                limit=limit,
                offset=offset,
                next=next_url,
                previous=previous_url,
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pokemon_public: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/public/pokemons/{identifier}", response_model=PokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_pokemon_public(request: Request, identifier: str):
    """Get pokemon details by ID or name (public endpoint)"""
    logger.info(f"Fetching pokemon (public): {identifier}")

    try:
        if identifier.isdigit():
            return await pokemon_service.get_pokemon_by_id(int(identifier))
        else:
            return await pokemon_service.get_pokemon_by_name(identifier.lower())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pokemons_public: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
