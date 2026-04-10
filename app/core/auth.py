from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.requests import Request
from typing import Optional, List
import os
from app.utils.logger import setup_logger
from app.core.config import get_api_keys

logger = setup_logger()

# API Key header name
API_KEY_NAME = "X-API-Key"

# Get API keys from settings
VALID_API_KEYS: List[str] = get_api_keys()

# Security scheme
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key and return it if valid.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The valid API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("API key missing in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing. Please provide a valid API key in the X-API-Key header",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Access denied.",
        )
    
    logger.debug(f"API key verified successfully")
    return api_key

# Optional: Create a dependency for optional auth (for public endpoints)
async def optional_auth(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional authentication that doesn't fail if no API key is provided.
    """
    if api_key and api_key in VALID_API_KEYS:
        return api_key
    return None