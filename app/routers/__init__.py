from core.config import main_config
from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

ACCESS_API_KEY = main_config.access_api_key


def check_api_key_access(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key is missing")

    if ACCESS_API_KEY != api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    return True
