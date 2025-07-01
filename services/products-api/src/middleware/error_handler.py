import logging
from typing import Any, Dict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

logger = logging.getLogger("api.errors")

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Gestionnaire global d'exceptions pour des réponses d'erreur cohérentes."""
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Erreurs HTTP FastAPI
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "http_error",
                    "request_id": request_id
                }
            }
        )
    
    # Erreurs de validation Pydantic
    if isinstance(exc, ValidationError):
        logger.warning(
            "Validation error",
            extra={"request_id": request_id, "errors": exc.errors()}
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation failed",
                    "type": "validation_error",
                    "details": exc.errors(),
                    "request_id": request_id
                }
            }
        )
    
    # Erreurs de base de données
    if isinstance(exc, IntegrityError):
        logger.error(
            "Database integrity error",
            extra={"request_id": request_id, "error": str(exc)},
            exc_info=True
        )
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": 409,
                    "message": "Data integrity constraint violation",
                    "type": "integrity_error",
                    "request_id": request_id
                }
            }
        )
    
    if isinstance(exc, SQLAlchemyError):
        logger.error(
            "Database error",
            extra={"request_id": request_id, "error": str(exc)},
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Database operation failed",
                    "type": "database_error",
                    "request_id": request_id
                }
            }
        )
    
    # Erreurs génériques
    logger.error(
        "Unhandled exception",
        extra={"request_id": request_id, "error": str(exc), "type": type(exc).__name__},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
                "request_id": request_id
            }
        }
    )

def create_error_response(status_code: int, message: str, error_type: str = "error", details: Any = None) -> Dict:
    """Créer une réponse d'erreur standardisée."""
    error_response = {
        "error": {
            "code": status_code,
            "message": message,
            "type": error_type
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    return error_response 