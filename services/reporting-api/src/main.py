from src.api.v1.router import api_router
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid
import os
from src.metrics_service import metrics_service, CONTENT_TYPE_LATEST
from src.metrics_middleware import MetricsMiddleware

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("reporting-api")

app = FastAPI(
    title="Reporting API",
    description="API RESTful de reporting et analytics - Architecture DDD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Middleware de logging avec traçage
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(f"🔍 [{request_id}] {request.method} {request.url} - Started")

    try:
        response = await call_next(request)
        process_time = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"✅ [{request_id}] {response.status_code} - Completed in {process_time}ms"
        )

        # Ajouter l'ID de requête aux headers
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ [{request_id}] Error after {process_time}ms: {str(e)}")
        raise


# Gestionnaire d'erreurs standardisé
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = str(uuid.uuid4())[:8]

    logger.warning(f"⚠️ [{request_id}] HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
                "request_id": request_id,
                "service": "reporting",
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())[:8]

    logger.error(f"💥 [{request_id}] Unhandled error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
                "request_id": request_id,
                "service": "reporting",
            }
        },
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter le middleware de métriques
app.add_middleware(MetricsMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize reporting API"""
    logger.info("🚀 Starting Reporting API with enhanced logging and error handling")
    logger.info("✅ Reporting API initialized - No local database required")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Reporting API")


@app.get("/")
async def root():
    logger.info("📋 Root endpoint accessed")
    return {
        "message": "Reporting API is running",
        "service": "reporting",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "RESTful API",
            "DDD Architecture",
            "Analytics & Reporting",
            "Structured Logging",
            "External Data Integration",
        ],
    }


@app.get("/health")
async def health_check():
    logger.debug("💚 Health check requested")
    return {
        "status": "healthy",
        "service": "reporting",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.get("/metrics")
async def get_metrics():
    """📊 Endpoint pour les métriques Prometheus"""
    logger.debug("📊 Metrics requested")
    metrics_data = metrics_service.get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
