from fastapi import APIRouter, Depends
from ..dependencies import api_token_auth
from ..services.cache_service import cache_service

router = APIRouter()

@router.get("/stats")
async def get_cache_stats(
    _: str = Depends(api_token_auth),
):
    """Get Redis cache statistics."""
    return cache_service.get_stats()

@router.post("/clear")
async def clear_cache(
    pattern: str = "*",
    _: str = Depends(api_token_auth),
):
    """Clear cache keys matching pattern."""
    cleared_count = cache_service.clear_pattern(pattern)
    return {
        "message": f"Cleared {cleared_count} keys matching pattern '{pattern}'",
        "cleared_count": cleared_count
    } 