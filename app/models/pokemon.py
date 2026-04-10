from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PokemonSprites(BaseModel):
    """Pokemon sprites model"""
    front_default: Optional[str] = None
    back_default: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "front_default": "https://raw.githubusercontent.com/...",
                "back_default": "https://raw.githubusercontent.com/..."
            }
        }

class PokemonResponse(BaseModel):
    """Pokemon response model"""
    id: int
    name: str
    height: int
    weight: int
    types: List[str]
    sprites: PokemonSprites
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "types": ["electric"],
                "sprites": {
                    "front_default": "https://raw.githubusercontent.com/...",
                    "back_default": "https://raw.githubusercontent.com/..."
                }
            }
        }

class PaginationMeta(BaseModel):
    """Pagination metadata model"""
    total: int
    limit: int
    offset: int
    next: Optional[str]
    previous: Optional[str]

class PokemonListResponse(BaseModel):
    """Pokemon list response model"""
    data: List[PokemonResponse]
    pagination: PaginationMeta