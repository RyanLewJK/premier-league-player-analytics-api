import os
from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY", "567")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key