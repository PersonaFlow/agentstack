from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from app.core.configuration import Settings
from app.core.exception import UnauthorizedException

API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
settings = Settings()

async def get_api_key(api_key_header: str = Security(api_key_header)):
    key = settings.PERSONAFLOW_API_KEY
    if key:
        if api_key_header == key:
            return api_key_header
        else:
            raise UnauthorizedException

