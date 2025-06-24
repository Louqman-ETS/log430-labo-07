from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from src.api.v1.api import api_router
from src.api.v1.errors import add_exception_handlers
from src.api.v1.middleware.metrics_middleware import MetricsMiddleware
from src.api.v1.services.metrics_service import metrics_service, CONTENT_TYPE_LATEST
from .logging_config import setup_logging, get_logger, log_api_call

# Setup logging before creating the app
setup_logging()
logger = get_logger("api")

# Configuration de l'application avec sécurité dans la documentation
app = FastAPI(
    title="LOG430-Labo-03 API",
    description="API RESTful pour le système de gestion de magasins avec architecture DDD",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration de la sécurité pour la documentation OpenAPI
app.openapi_schema = None  # Force regeneration


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="LOG430-Labo-03 API",
        version="1.0.0",
        description="API RESTful pour le système de gestion de magasins avec architecture DDD",
        routes=app.routes,
    )

    # Ajouter la configuration de sécurité
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Token",
            "description": "API Token pour l'authentification",
        }
    }

    # Appliquer la sécurité à tous les endpoints par défaut
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"APIKeyHeader": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Add exception handlers
add_exception_handlers(app)


# Middleware pour logger les requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests and responses"""
    start_time = time.time()

    # Log incoming request
    endpoint_logger = get_logger("api.endpoints")
    endpoint_logger.info(f"Incoming request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate response time
    process_time = time.time() - start_time

    # Log API call with performance metrics
    log_api_call(
        endpoint_logger,
        method=request.method,
        endpoint=str(request.url.path),
        status_code=response.status_code,
        response_time=process_time,
    )

    # Add performance header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Inclure les routes de l'API v1
app.include_router(api_router, prefix="/api/v1")


# Endpoint de santé (sans authentification)
@app.get("/health", tags=["health"])
async def health_check():
    """Check API health status."""
    return {"status": "healthy", "message": "API is running"}


# Endpoint des métriques Prometheus (sans authentification)
@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """Expose Prometheus metrics."""
    metrics_data = metrics_service.get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Endpoint de documentation des erreurs
@app.get("/api/v1/errors", tags=["documentation"])
async def error_documentation():
    """Documentation des codes d'erreur de l'API."""
    return {
        "error_codes": {
            "AUTHENTICATION_ERROR": {
                "status": 401,
                "description": "Token d'authentification invalide ou manquant",
                "example": "Invalid or missing API Token",
            },
            "VALIDATION_ERROR": {
                "status": 400,
                "description": "Erreur de validation des données d'entrée",
                "example": "Field 'email' is required",
            },
            "NOT_FOUND": {
                "status": 404,
                "description": "Ressource non trouvée",
                "example": "Product with identifier 123 not found",
            },
            "DUPLICATE_RESOURCE": {
                "status": 409,
                "description": "Tentative de création d'une ressource qui existe déjà",
                "example": "Product with code 'ABC123' already exists",
            },
            "BUSINESS_LOGIC_ERROR": {
                "status": 422,
                "description": "Erreur de logique métier",
                "example": "Insufficient stock quantity",
            },
            "INTERNAL_ERROR": {
                "status": 500,
                "description": "Erreur interne du serveur",
                "example": "An internal server error occurred",
            },
        },
        "response_format": {
            "timestamp": "2024-01-01T00:00:00Z",
            "status": 400,
            "error": "Bad Request",
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {},
            "path": "/api/v1/products",
        },
    }
