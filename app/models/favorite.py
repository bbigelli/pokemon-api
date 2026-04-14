from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
from app.api.schemas.favorite import FavoritePokemonResponse


class FavoritePokemon(Base):
    """Model for favorite pokemons stored in database"""

    __tablename__ = "favorite_pokemons"

    id = Column(Integer, primary_key=True, index=True)
    pokemon_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    nickname = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_schema(self) -> FavoritePokemonResponse:
        """Convert model to Pydantic schema"""
        # Converter para dicionário primeiro
        return FavoritePokemonResponse.model_validate(self.__dict__)

    def __repr__(self):
        return f"<FavoritePokemon(id={self.pokemon_id}, name={self.name})>"
