import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

from .errors import AuthenticationError

load_dotenv()

# Configuration du token API
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN environment variable is required")

# Schema pour l'authentification par header
api_key_header = APIKeyHeader(
    name="X-API-Token", description="API Token for authentication"
)


async def api_token_auth(api_token: str = Depends(api_key_header)) -> str:
    """
    Vérifie l'authentification par token API

    Args:
        api_token: Token fourni dans le header X-API-Token

    Returns:
        str: Le token validé

    Raises:
        AuthenticationError: Si le token est invalide ou manquant
    """
    if not api_token:
        raise AuthenticationError("API Token is required")

    if api_token != API_TOKEN:
        raise AuthenticationError("Invalid API Token")

    return api_token


def get_current_token(token: str = Depends(api_token_auth)) -> str:
    """
    Obtient le token actuel (après validation)

    Args:
        token: Token validé

    Returns:
        str: Le token validé
    """
    return token
