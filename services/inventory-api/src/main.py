import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid
import os
from src.database import engine, Base
from src.api.v1.router import api_router
from src.init_db import init_database

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("inventory-api")

# ID de l'instance pour le load balancing
INSTANCE_ID = os.getenv("INSTANCE_ID", "inventory-api-default")

app = FastAPI(
    title="Inventory API",
    description="API RESTful de gestion des produits, catégories et stocks - Architecture DDD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Middleware de logging avec traçage et ID d'instance
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(f"🔍 [{INSTANCE_ID}][{request_id}] {request.method} {request.url} - Started")

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
        logger.error(f"❌ [{INSTANCE_ID}][{request_id}] Error after {process_time}ms: {str(e)}")
        raise


# Gestionnaire d'erreurs standardisé
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])

    logger.warning(f"⚠️ [{INSTANCE_ID}][{request_id}] HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
                "service": "inventory",
                "instance": INSTANCE_ID,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])

    logger.error(f"💥 [{INSTANCE_ID}][{request_id}] Unhandled error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
                "service": "inventory",
                "instance": INSTANCE_ID,
                "request_id": request_id,
            }
        },
    )


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes API
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialise la base de données avec des données d'exemple si vide"""

    logger.info(f"🚀 Starting Inventory API [{INSTANCE_ID}] with enhanced logging and error handling")

    # Créer les tables seulement si on n'est pas en mode test
    if not os.getenv("TESTING"):
        try:
            # Créer les tables de manière idempotente
            Base.metadata.create_all(bind=engine, checkfirst=True)
            logger.info(f"✅ [{INSTANCE_ID}] Database tables verified/created")

            # Seule la première instance initialise les données
            if INSTANCE_ID == "inventory-api-1":
                try:
                    init_database()
                    logger.info(f"✅ [{INSTANCE_ID}] Database initialized successfully (primary instance)")
                except Exception as e:
                    # Si l'initialisation échoue, ce n'est pas grave (données probablement déjà présentes)
                    logger.warning(f"⚠️ [{INSTANCE_ID}] Database initialization skipped or failed: {e}")
            else:
                logger.info(f"✅ [{INSTANCE_ID}] Database initialization skipped (secondary instance)")
                
        except Exception as e:
            logger.error(f"❌ [{INSTANCE_ID}] Failed to setup database: {e}", exc_info=True)
            # Ne pas faire échouer le démarrage pour les problèmes de DB concurrentiels
            logger.warning(f"⚠️ [{INSTANCE_ID}] Continuing startup despite database setup issues")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage lors de l'arrêt"""
    logger.info(f"🛑 [{INSTANCE_ID}] Shutting down Inventory API")


@app.get("/")
async def root():
    logger.info(f"📋 [{INSTANCE_ID}] Root endpoint accessed")
    return {
        "message": "Inventory API is running",
        "service": "inventory",
        "instance": INSTANCE_ID,
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "RESTful API",
            "DDD Architecture",
            "Product Management",
            "Stock Management",
            "Inventory Tracking",
            "Stock Alerts",
            "Structured Logging",
            "Load Balancing Support",
        ],
    }


@app.get("/health")
async def health_check():
    logger.debug(f"💚 [{INSTANCE_ID}] Health check requested")
    return {
        "status": "healthy",
        "service": "inventory",
        "instance": INSTANCE_ID,
        "version": "1.0.0",
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
