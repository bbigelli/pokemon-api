from fastapi import Depends
from app.core.auth import verify_api_key

# Dependency for protected endpoints
require_auth = Depends(verify_api_key)
