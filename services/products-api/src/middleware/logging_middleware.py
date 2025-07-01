import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Générer un ID unique pour la requête
        request_id = str(uuid.uuid4())[:8]
        
        # Log de la requête entrante
        start_time = time.time()
        
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        # Traiter la requête
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log de la réponse
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": round(process_time * 1000, 2),  # en millisecondes
                }
            )
            
            # Ajouter l'ID de requête aux headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": round(process_time * 1000, 2),
                },
                exc_info=True
            )
            raise 