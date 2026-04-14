from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.auth import verify_api_key
from app.core.rate_limit import limiter
from app.core.config import settings
from app.services.favorite_service import favorite_service
from app.api.schemas.favorite import (
    FavoritePokemonCreate,
    FavoritePokemonUpdate,
    FavoritePokemonResponse,
    FavoritePokemonListResponse,
)
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()


@router.post(
    "/favorites",
    response_model=FavoritePokemonResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT)
async def create_favorite(
    request: Request,
    favorite_data: FavoritePokemonCreate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Add a pokemon to favorites (CREATE operation)

    - Requires valid API key
    - Pokemon must exist in PokeAPI
    - Pokemon cannot be already in favorites
    """
    logger.info(f"Creating favorite pokemon: {favorite_data.pokemon_id}")
    return await favorite_service.create_favorite(db, favorite_data)


@router.get("/favorites", response_model=FavoritePokemonListResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_favorites(
    request: Request,
    api_key: str = Depends(verify_api_key),
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    only_favorites: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """
    Get list of favorite pokemons (READ operation - list)

    - Requires valid API key
    - Supports pagination
    - Can filter by is_favorite status
    """
    logger.info(f"Fetching favorites - limit: {limit}, offset: {offset}")

    favorites, total = favorite_service.get_favorites(db, offset, limit, only_favorites)

    return FavoritePokemonListResponse(
        data=favorites, total=total, limit=limit, offset=offset
    )


@router.get("/favorites/{favorite_id}", response_model=FavoritePokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_favorite_by_id(
    request: Request,
    favorite_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Get a specific favorite pokemon by its database ID (READ operation - single)

    - Requires valid API key
    """
    logger.info(f"Fetching favorite by ID: {favorite_id}")
    return favorite_service.get_favorite_by_id(db, favorite_id)


@router.get("/favorites/pokemon/{pokemon_id}", response_model=FavoritePokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def get_favorite_by_pokemon_id(
    request: Request,
    pokemon_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Get a favorite pokemon by its PokeAPI ID

    - Requires valid API key
    """
    logger.info(f"Fetching favorite by pokemon ID: {pokemon_id}")
    favorite = favorite_service.get_favorite_by_pokemon_id(db, pokemon_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokemon {pokemon_id} not found in favorites",
        )
    return favorite


@router.put("/favorites/{favorite_id}", response_model=FavoritePokemonResponse)
@limiter.limit(settings.RATE_LIMIT)
async def update_favorite(
    request: Request,
    favorite_id: int,
    update_data: FavoritePokemonUpdate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Update a favorite pokemon (UPDATE operation)

    - Requires valid API key
    - Can update nickname, notes, is_favorite status
    """
    logger.info(f"Updating favorite ID: {favorite_id}")
    return favorite_service.update_favorite(db, favorite_id, update_data)


@router.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.RATE_LIMIT)
async def delete_favorite(
    request: Request,
    favorite_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Delete a favorite pokemon (DELETE operation)

    - Requires valid API key
    """
    logger.info(f"Deleting favorite ID: {favorite_id}")
    favorite_service.delete_favorite(db, favorite_id)
    return None
