from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from ..services.metrics_service import metrics_service


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Commencer le chronométrage
        start_time = time.time()

        # Incrémenter les requêtes actives
        metrics_service.increment_active_requests()

        try:
            # Traiter la requête
            response = await call_next(request)

            # Calculer la durée
            duration = time.time() - start_time

            # Extraire l'endpoint (sans paramètres de query)
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code

            # Enregistrer les métriques
            metrics_service.record_request(method, endpoint, status_code, duration)

            return response

        except Exception as e:
            # En cas d'erreur, enregistrer l'erreur
            duration = time.time() - start_time
            endpoint = request.url.path
            method = request.method

            # Enregistrer l'erreur
            metrics_service.record_error(type(e).__name__, endpoint)
            metrics_service.record_request(method, endpoint, 500, duration)

            # Relancer l'exception
            raise e

        finally:
            # Décrémenter les requêtes actives
            metrics_service.decrement_active_requests()
