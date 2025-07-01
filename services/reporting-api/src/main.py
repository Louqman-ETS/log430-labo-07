from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("reporting-api")

from .database import engine, get_db, Base
from .models import Sale, SaleLine, StoreStock, CentralStock, RestockingRequest
from .api.v1.router import api_router
from .init_db import init_database

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reporting API",
    description="API RESTful de reporting et analytics - Architecture DDD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        
        logger.info(f"✅ [{request_id}] {response.status_code} - Completed in {process_time}ms")
        
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
                "service": "reporting"
            }
        }
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
                "service": "reporting"
            }
        }
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data if empty"""
    logger.info("🚀 Starting Reporting API with enhanced logging and error handling")
    max_retries = 30
    retry_interval = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"📊 Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
            # Créer les tables
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
            
            # Initialiser les données
            init_database()
            logger.info("✅ Reporting database initialized")
            break
            
        except Exception as e:
            logger.warning(f"❌ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logger.error("❌ Failed to initialize database after all retries")
                raise

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
        "features": ["RESTful API", "DDD Architecture", "Analytics & Reporting", "Structured Logging"]
    }

@app.get("/health")
async def health_check():
    logger.debug("💚 Health check requested")
    return {
        "status": "healthy",
        "service": "reporting",
        "version": "1.0.0",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005) 