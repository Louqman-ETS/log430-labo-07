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

logger = logging.getLogger("stock-api")

app = FastAPI(
    title="Stock API",
    description="API RESTful de gestion des stocks - Architecture DDD",
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
                "service": "stock"
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
                "service": "stock"
            }
        }
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Stock API with enhanced logging and error handling")
    logger.info("📦 Stock service ready for inventory management")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Stock API")

# Routes RESTful pour la gestion des stocks
@app.put("/api/v1/products/{product_id}/stock/reduce")
async def reduce_stock(product_id: int, quantity: int):
    """Réduire le stock d'un produit (appelé lors d'une vente)"""
    logger.info(f"📦 Reducing stock for product {product_id} by quantity {quantity}")
    
    # TODO: Implémenter la logique de réduction de stock
    # Pour l'instant, on simule le succès
    return {
        "success": True,
        "product_id": product_id,
        "reduced_quantity": quantity,
        "message": f"Stock reduced by {quantity} for product {product_id}",
        "service": "stock"
    }

@app.put("/api/v1/products/{product_id}/stock/increase")
async def increase_stock(product_id: int, quantity: int):
    """Augmenter le stock d'un produit (réapprovisionnement)"""
    logger.info(f"📦 Increasing stock for product {product_id} by quantity {quantity}")
    
    # TODO: Implémenter la logique d'augmentation de stock
    return {
        "success": True,
        "product_id": product_id,
        "increased_quantity": quantity,
        "message": f"Stock increased by {quantity} for product {product_id}",
        "service": "stock"
    }

@app.get("/api/v1/products/{product_id}/stock")
async def get_stock(product_id: int):
    """Obtenir le niveau de stock d'un produit"""
    logger.info(f"📦 Getting stock level for product {product_id}")
    
    # TODO: Implémenter la récupération du stock
    return {
        "product_id": product_id,
        "stock_quantity": 50,  # Valeur simulée
        "alert_threshold": 10,
        "status": "normal",
        "service": "stock"
    }

@app.get("/api/v1/stock/alerts")
async def get_stock_alerts():
    """Obtenir tous les produits avec un stock faible"""
    logger.info("📦 Getting stock alerts")
    
    # TODO: Implémenter la récupération des alertes
    return {
        "alerts": [],  # Vide pour l'instant
        "total_alerts": 0,
        "service": "stock"
    }

@app.get("/")
async def root():
    logger.info("📋 Root endpoint accessed")
    return {
        "message": "Stock API is running",
        "service": "stock",
        "version": "1.0.0",
        "docs": "/docs",
        "features": ["RESTful API", "DDD Architecture", "Inventory Management", "Structured Logging"]
    }

@app.get("/health")
async def health_check():
    logger.debug("💚 Health check requested")
    return {
        "status": "healthy",
        "service": "stock",
        "version": "1.0.0",
        "timestamp": time.time()
    } 