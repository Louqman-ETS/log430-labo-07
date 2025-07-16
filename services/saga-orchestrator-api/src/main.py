import uvicorn
import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.database import engine, Base
from src.api.v1.router import api_router
from src.init_db import init_database
from src.metrics_service import metrics_service, CONTENT_TYPE_LATEST
from src.metrics_middleware import MetricsMiddleware

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("saga-orchestrator")

# ID de l'instance pour le load balancing
INSTANCE_ID = os.getenv("INSTANCE_ID", "saga-orchestrator-1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info(f"🚀 Starting Saga Orchestrator API [{INSTANCE_ID}]")
    
    # Créer les tables si pas en mode test
    if not os.getenv("TESTING"):
        try:
            # Créer les tables de manière idempotente
            Base.metadata.create_all(bind=engine, checkfirst=True)
            logger.info(f"✅ [{INSTANCE_ID}] Database tables verified/created")
            
            # Initialiser les données si nécessaire
            try:
                init_database()
                logger.info(f"✅ [{INSTANCE_ID}] Database initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ [{INSTANCE_ID}] Database initialization skipped: {e}")
                
        except Exception as e:
            logger.error(f"❌ [{INSTANCE_ID}] Failed to setup database: {e}", exc_info=True)
    
    # Définir le statut de santé comme bon
    metrics_service.set_health_status(True)
    
    yield
    
    # Shutdown
    logger.info(f"🛑 Stopping Saga Orchestrator API [{INSTANCE_ID}]")
    metrics_service.set_health_status(False)


# Créer l'application FastAPI
app = FastAPI(
    title="🔄 Saga Orchestrator API",
    description="Service d'orchestration de sagas pour la coordination de transactions distribuées",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Middleware de logging avec traçage et ID d'instance
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(
        f"🔍 [{INSTANCE_ID}][{request_id}] {request.method} {request.url} - Started"
    )

    try:
        response = await call_next(request)
        process_time = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"✅ [{INSTANCE_ID}][{request_id}] {response.status_code} - Completed in {process_time}ms"
        )

        # Ajouter l'ID de requête et l'instance aux headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Instance-ID"] = INSTANCE_ID
        return response

    except Exception as e:
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"❌ [{INSTANCE_ID}][{request_id}] Error after {process_time}ms: {str(e)}"
        )
        raise


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter le middleware de métriques
app.add_middleware(MetricsMiddleware)

# Inclure les routes API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint racine"""
    logger.info(f"📋 [{INSTANCE_ID}] Root endpoint accessed")
    return {
        "message": "Saga Orchestrator API is running",
        "service": "saga-orchestrator",
        "instance": INSTANCE_ID,
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Saga Pattern Implementation",
            "Synchronous Orchestration",
            "Compensation/Rollback",
            "Event Sourcing",
            "Prometheus Metrics",
            "Structured Logging",
            "Load Balancing Support",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug(f"💚 [{INSTANCE_ID}] Health check requested")
    return {
        "status": "healthy",
        "service": "saga-orchestrator",
        "instance": INSTANCE_ID,
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.get("/metrics", response_class=Response)
async def get_metrics():
    """Endpoint pour les métriques Prometheus"""
    metrics_data = metrics_service.get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global d'exceptions"""
    logger.error(f"❌ [{INSTANCE_ID}] Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "instance": INSTANCE_ID,
        }
    )


if __name__ == "__main__":
    # Configuration pour le développement local
    port = int(os.getenv("PORT", "8004"))
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 