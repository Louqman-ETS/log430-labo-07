from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid
import os
from contextlib import asynccontextmanager

from src.database import engine, Base
from src.api.v1.router import api_router
from src.init_db import init_database

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage du service Ecommerce API")

    # Créer les tables si pas en mode test
    if not os.getenv("TESTING"):
        Base.metadata.create_all(bind=engine)
        logger.info("📊 Tables de base de données créées")

        # Initialiser les données de test
        init_database()
        logger.info("✅ Données de test initialisées")

    yield

    # Shutdown
    logger.info("🛑 Arrêt du service Ecommerce API")


# Créer l'application FastAPI
app = FastAPI(
    title="🛍️ Ecommerce API",
    description="Service unifié de gestion des clients, paniers et commandes",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware pour le logging et timing des requêtes
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware pour le logging structuré avec Request-ID"""
    start_time = time.time()

    # Générer ou récupérer le Request-ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Log de la requête entrante
    logger.info(f"🔍 [{request_id}] {request.method} {request.url.path} - Début")

    # Traiter la requête
    try:
        response = await call_next(request)

        # Calculer le temps de traitement
        process_time = time.time() - start_time

        # Ajouter les headers de réponse
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log de la réponse
        logger.info(
            f"✅ [{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Temps: {process_time:.3f}s"
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ [{request_id}] {request.method} {request.url.path} - "
            f"Erreur: {str(e)} - Temps: {process_time:.3f}s"
        )
        raise


# Gestionnaire d'erreurs global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'erreurs HTTP personnalisé"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Si le detail est déjà un dict, l'utiliser tel quel
    if isinstance(exc.detail, dict):
        error_detail = exc.detail
    else:
        # Sinon, créer un format standardisé
        error_detail = {
            "error": "HTTP Exception",
            "message": exc.detail,
            "service": "ecommerce-api",
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail,
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs générales"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    logger.error(f"❌ Erreur non gérée [{request_id}]: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Une erreur interne s'est produite",
            "service": "ecommerce-api",
        },
        headers={"X-Request-ID": request_id},
    )


# Routes de base
@app.get("/")
async def root():
    """🏠 Point d'entrée de l'API"""
    return {
        "service": "ecommerce-api",
        "version": "1.0.0",
        "description": "Service unifié de gestion des clients, paniers et commandes",
        "status": "running",
        "domains": ["customers", "carts", "orders"],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """🏥 Vérification de l'état du service"""
    return {"status": "healthy", "service": "ecommerce-api", "timestamp": time.time()}


# Inclure les routes de l'API
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
