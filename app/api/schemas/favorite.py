from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FavoritePokemonBase(BaseModel):
    """Base schema for favorite pokemon"""
    pokemon_id: int = Field(..., ge=1, description="Pokemon ID from PokeAPI")
    name: str = Field(..., min_length=1, max_length=100, description="Pokemon name")
    nickname: Optional[str] = Field(None, max_length=100, description="Custom nickname")
    notes: Optional[str] = Field(None, description="Personal notes about this pokemon")
    is_favorite: bool = Field(default=True, description="Whether is marked as favorite")

    class Config:
        json_schema_extra = {
            "example": {
                "pokemon_id": 25,
                "name": "pikachu",
                "nickname": "Pika",
                "notes": "My favorite electric pokemon",
                "is_favorite": True
            }
        }


class FavoritePokemonCreate(FavoritePokemonBase):
    """Schema for creating a favorite pokemon"""
    pass


class FavoritePokemonUpdate(BaseModel):
    """Schema for updating a favorite pokemon"""
    nickname: Optional[str] = Field(None, max_length=100, description="Custom nickname")
    notes: Optional[str] = Field(None, description="Personal notes about this pokemon")
    is_favorite: Optional[bool] = Field(None, description="Whether is marked as favorite")

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "Pikachu Jr",
                "notes": "Updated notes",
                "is_favorite": True
            }
        }


class FavoritePokemonResponse(FavoritePokemonBase):
    """Schema for favorite pokemon response"""
    id: int = Field(..., description="Database ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "pokemon_id": 25,
                "name": "pikachu",
                "nickname": "Pika",
                "notes": "My favorite electric pokemon",
                "is_favorite": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class FavoritePokemonListResponse(BaseModel):
    """Schema for list of favorite pokemons"""
    data: list[FavoritePokemonResponse] = Field(..., description="List of favorites")
    total: int = Field(..., description="Total number of favorites")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "total": 0,
                "limit": 20,
                "offset": 0
            }
        }