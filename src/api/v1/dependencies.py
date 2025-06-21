from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_TOKEN_ENV_VAR = "API_TOKEN"
API_TOKEN_SCHEME = APIKeyHeader(name="X-API-Token", auto_error=False)


def get_api_token() -> str:
    api_token = os.getenv(API_TOKEN_ENV_VAR)
    if not api_token:
        raise RuntimeError(f"{API_TOKEN_ENV_VAR} environment variable not set")
    return api_token


def api_token_auth(
    api_token_header: str = Depends(API_TOKEN_SCHEME),
    valid_api_token: str = Depends(get_api_token),
):
    if not api_token_header or api_token_header != valid_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Token",
        )
