from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.models.favorite import FavoritePokemon
from app.api.schemas.favorite import FavoritePokemonCreate, FavoritePokemonUpdate
from app.services.pokemon_service import pokemon_service
from app.utils.logger import setup_logger

logger = setup_logger()

class FavoriteService:
    """Service for managing favorite pokemons in database"""
    
    async def create_favorite(
        self, 
        db: Session, 
        favorite_data: FavoritePokemonCreate
    ) -> FavoritePokemon:
        """Create a new favorite pokemon"""
        # Check if pokemon exists in PokeAPI
        try:
            pokemon = await pokemon_service.get_pokemon_by_id(favorite_data.pokemon_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokemon with ID {favorite_data.pokemon_id} not found in PokeAPI"
            )
        
        # Check if already exists in favorites
        existing = db.query(FavoritePokemon).filter(
            FavoritePokemon.pokemon_id == favorite_data.pokemon_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Pokemon {pokemon.name} is already in favorites"
            )
        
        # Create new favorite
        db_favorite = FavoritePokemon(
            pokemon_id=favorite_data.pokemon_id,
            name=pokemon.name,
            nickname=favorite_data.nickname,
            notes=favorite_data.notes,
            is_favorite=True
        )
        
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        
        logger.info(f"Added pokemon {pokemon.name} to favorites")
        return db_favorite
    
    def get_favorites(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        only_favorites: bool = True
    ) -> Tuple[List[FavoritePokemon], int]:
        """Get list of favorite pokemons"""
        query = db.query(FavoritePokemon)
        
        if only_favorites:
            query = query.filter(FavoritePokemon.is_favorite == True)
        
        total = query.count()
        favorites = query.order_by(desc(FavoritePokemon.created_at)).offset(skip).limit(limit).all()
        
        return favorites, total
    
    def get_favorite_by_id(self, db: Session, favorite_id: int) -> FavoritePokemon:
        """Get favorite pokemon by ID"""
        favorite = db.query(FavoritePokemon).filter(FavoritePokemon.id == favorite_id).first()
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Favorite pokemon with ID {favorite_id} not found"
            )
        return favorite
    
    def get_favorite_by_pokemon_id(self, db: Session, pokemon_id: int) -> Optional[FavoritePokemon]:
        """Get favorite pokemon by pokemon_id"""
        return db.query(FavoritePokemon).filter(FavoritePokemon.pokemon_id == pokemon_id).first()
    
    def update_favorite(
        self, 
        db: Session, 
        favorite_id: int, 
        update_data: FavoritePokemonUpdate
    ) -> FavoritePokemon:
        """Update a favorite pokemon"""
        favorite = self.get_favorite_by_id(db, favorite_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(favorite, key, value)
        
        db.commit()
        db.refresh(favorite)
        
        logger.info(f"Updated favorite pokemon ID {favorite_id}")
        return favorite
    
    def delete_favorite(self, db: Session, favorite_id: int) -> None:
        """Delete a favorite pokemon"""
        favorite = self.get_favorite_by_id(db, favorite_id)
        
        db.delete(favorite)
        db.commit()
        
        logger.info(f"Deleted favorite pokemon ID {favorite_id}")

favorite_service = FavoriteService()