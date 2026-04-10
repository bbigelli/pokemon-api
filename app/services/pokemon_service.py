import httpx
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.cache import cache_service
from app.models.pokemon import PokemonResponse, PokemonSprites
from app.utils.logger import setup_logger

logger = setup_logger()

class PokemonService:
    """Service for interacting with PokeAPI"""
    
    def __init__(self):
        self.base_url = settings.POKEAPI_BASE_URL
        self.timeout = settings.POKEAPI_TIMEOUT
    
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request to PokeAPI"""
        cache_key = f"request:{url}"
        
        # Try to get from cache
        cached_response = cache_service.get(cache_key)
        if cached_response:
            logger.debug(f"Cache hit for {url}")
            return cached_response
        
        # Make request to PokeAPI
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Cache the response
                cache_service.set(cache_key, data)
                logger.debug(f"Cached response for {url}")
                
                return data
            except httpx.TimeoutException:
                logger.error(f"Timeout error for {url}")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="PokeAPI request timeout"
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error for {url}: {e}")
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Pokemon not found"
                    )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"PokeAPI error: {e.response.status_code}"
                )
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
    
    async def get_pokemon_list(self, limit: int, offset: int) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated list of pokemons"""
        url = f"{self.base_url}/pokemon?limit={limit}&offset={offset}"
        data = await self._make_request(url)
        
        pokemons = []
        for pokemon in data.get('results', []):
            # Get detailed info for each pokemon
            detail = await self._make_request(pokemon['url'])
            pokemons.append(detail)
        
        return pokemons, data.get('count', 0)
    
    async def get_pokemon_by_id(self, pokemon_id: int) -> PokemonResponse:
        """Get pokemon details by ID"""
        url = f"{self.base_url}/pokemon/{pokemon_id}"
        data = await self._make_request(url)
        return self._transform_pokemon_data(data)
    
    async def get_pokemon_by_name(self, name: str) -> PokemonResponse:
        """Get pokemon details by name"""
        url = f"{self.base_url}/pokemon/{name.lower()}"
        data = await self._make_request(url)
        return self._transform_pokemon_data(data)
    
    def _transform_pokemon_data(self, data: Dict[str, Any]) -> PokemonResponse:
        """Transform PokeAPI response to our format"""
        return PokemonResponse(
            id=data['id'],
            name=data['name'],
            height=data['height'],
            weight=data['weight'],
            types=[t['type']['name'] for t in data['types']],
            sprites=PokemonSprites(
                front_default=data['sprites'].get('front_default'),
                back_default=data['sprites'].get('back_default')
            )
        )

pokemon_service = PokemonService()