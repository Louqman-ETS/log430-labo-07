import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.metrics_service import metrics_service
import logging

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware pour collecter les métriques HTTP"""

    async def dispatch(self, request: Request, call_next):
        # Générer un ID de requête unique
        request_id = str(uuid.uuid4())[:8]
        
        # Enregistrer le début de la requête
        start_time = time.time()
        metrics_service.start_request(request_id)
        
        try:
            # Traiter la requête
            response = await call_next(request)
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Extraire les informations de la requête
            method = request.method
            endpoint = self._get_endpoint_pattern(request)
            status_code = response.status_code
            
            # Enregistrer les métriques
            metrics_service.record_request(method, endpoint, status_code, duration)
            
            # Ajouter les headers de response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            # Calculer la durée même en cas d'erreur
            duration = time.time() - start_time
            
            # Enregistrer l'erreur
            method = request.method
            endpoint = self._get_endpoint_pattern(request)
            metrics_service.record_request(method, endpoint, 500, duration)
            metrics_service.record_error("internal_error", endpoint)
            
            logger.error(f"❌ Request {request_id} failed: {e}")
            raise
            
        finally:
            # Marquer la fin de la requête
            metrics_service.end_request(request_id)
    
    def _get_endpoint_pattern(self, request: Request) -> str:
        """Extrait le pattern d'endpoint de la requête"""
        path = request.url.path
        
        # Normaliser les patterns d'URL pour les métriques
        if path.startswith("/api/v1/sagas/"):
            if path.endswith("/status"):
                return "/api/v1/sagas/{saga_id}/status"
            elif path.endswith("/events"):
                return "/api/v1/sagas/{saga_id}/events"
            elif len(path.split("/")) == 5:  # /api/v1/sagas/{saga_id}
                return "/api/v1/sagas/{saga_id}"
            else:
                return "/api/v1/sagas/"
        
        # Autres patterns communs
        if path == "/health":
            return "/health"
        elif path == "/metrics":
            return "/metrics"
        elif path.startswith("/docs"):
            return "/docs"
        elif path.startswith("/openapi"):
            return "/openapi.json"
        
        return path 