import json
import logging
import os
from typing import Any, Optional, Union
from functools import wraps
from decimal import Decimal

import redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


def json_serializer(obj):
    """Serializer personnalisé pour JSON qui gère les types Decimal"""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class CacheService:
    """Service de cache Redis pour optimiser les performances des endpoints critiques"""

    def __init__(self):
        self.redis_client = None
        self.enabled = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))

            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info(
                f"Redis cache initialized successfully at {redis_host}:{redis_port}"
            )

        except (ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"Redis cache unavailable: {e}. Operating without cache.")
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                # Import ici pour éviter les imports circulaires
                from .metrics_service import record_cache_operation

                record_cache_operation("get", "hit")
                return json.loads(value)
            else:
                from .metrics_service import record_cache_operation

                record_cache_operation("get", "miss")
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            from .metrics_service import record_cache_operation

            record_cache_operation("get", "error")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Store value in cache with TTL (default 5 minutes)"""
        if not self.enabled:
            return False

        try:
            # Convertir les objets Pydantic en dictionnaires JSON
            if hasattr(value, "model_dump"):
                # Pour les modèles Pydantic V2
                serialized_value = json.dumps(
                    value.model_dump(), default=json_serializer
                )
            elif hasattr(value, "dict"):
                # Pour les modèles Pydantic V1
                serialized_value = json.dumps(value.dict(), default=json_serializer)
            elif hasattr(value, "__dict__"):
                # Pour les autres objets avec attributs
                serialized_value = json.dumps(value.__dict__, default=json_serializer)
            else:
                # Pour les types basiques (dict, list, etc.)
                serialized_value = json.dumps(value, default=json_serializer)

            result = self.redis_client.setex(key, ttl, serialized_value)
            from .metrics_service import record_cache_operation

            record_cache_operation("set", "success" if result else "failed")
            return result
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            from .metrics_service import record_cache_operation

            record_cache_operation("set", "error")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False, "message": "Redis cache disabled"}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0,
                "memory_used": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": True, "error": str(e)}


# Instance globale du service de cache
cache_service = CacheService()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Décorateur pour mettre en cache les résultats de fonctions

    Args:
        ttl: Time to live en secondes (default 5 minutes)
        key_prefix: Préfixe pour la clé de cache
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Générer une clé de cache basée sur la fonction et ses arguments
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key = f"{key_prefix}:{func_name}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Essayer de récupérer depuis le cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Exécuter la fonction et mettre en cache le résultat
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, result cached")

            return result

        return wrapper

    return decorator


def cache_key_for_request(endpoint: str, params: dict = None) -> str:
    """Générer une clé de cache pour une requête donnée"""
    instance_id = os.getenv("INSTANCE_ID", "unknown")
    key = f"api:{instance_id}:{endpoint}"
    if params:
        param_str = ":".join([f"{k}={v}" for k, v in sorted(params.items())])
        key += f":{param_str}"
    return key
