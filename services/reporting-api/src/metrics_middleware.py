from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from .metrics_service import metrics_service

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware pour collecter automatiquement les métriques Prometheus"""

    async def dispatch(self, request: Request, call_next):
        # Démarrer le timer et incrémenter les requêtes actives
        start_time = time.time()
        metrics_service.increment_active_requests()

        # Normaliser le chemin pour éviter trop de cardinalité
        endpoint = self._normalize_endpoint(request.url.path)

        try:
            # Traiter la requête
            response = await call_next(request)

            # Calculer la durée
            duration = time.time() - start_time

            # Enregistrer la requête
            metrics_service.record_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
            )

            # Enregistrer les erreurs si nécessaire
            if response.status_code >= 400:
                error_type = self._get_error_type(response.status_code)
                metrics_service.record_error(error_type, endpoint)

            return response

        except Exception as e:
            # Enregistrer l'erreur
            duration = time.time() - start_time
            metrics_service.record_request(
                method=request.method,
                endpoint=endpoint,
                status_code=500,
                duration=duration,
            )
            metrics_service.record_error("internal_error", endpoint)
            raise

        finally:
            # Décrémenter les requêtes actives
            metrics_service.decrement_active_requests()

    def _normalize_endpoint(self, path: str) -> str:
        """Normalise le chemin pour éviter trop de cardinalité dans les métriques"""
        # Remplacer les IDs par des placeholders
        import re

        # Patterns courants pour les IDs
        path = re.sub(r"/\d+", "/{id}", path)
        path = re.sub(r"/[a-f0-9-]{36}", "/{uuid}", path)  # UUID
        path = re.sub(r"/[a-f0-9]{24}", "/{objectid}", path)  # MongoDB ObjectId

        # Limiter la longueur
        if len(path) > 50:
            path = path[:47] + "..."

        return path

    def _get_error_type(self, status_code: int) -> str:
        """Détermine le type d'erreur basé sur le code de statut"""
        if status_code == 400:
            return "bad_request"
        elif status_code == 401:
            return "unauthorized"
        elif status_code == 403:
            return "forbidden"
        elif status_code == 404:
            return "not_found"
        elif status_code == 422:
            return "validation_error"
        elif status_code == 429:
            return "rate_limit"
        elif 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown_error"
