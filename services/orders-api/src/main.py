from fastapi import FastAPI, Request, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import time
import uuid
import os
import httpx
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from .database import engine, Base, get_db
from . import models, schemas

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration des services externes
CART_API_URL = os.getenv("CART_API_URL", "http://cart-api:8007")
PRODUCTS_API_URL = os.getenv("PRODUCTS_API_URL", "http://products-api:8001")
STOCK_API_URL = os.getenv("STOCK_API_URL", "http://stock-api:8004")
SALES_API_URL = os.getenv("SALES_API_URL", "http://sales-api:8003")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage du service Orders API")
    
    # Créer les tables si pas en mode test
    if not os.getenv("TESTING"):
        Base.metadata.create_all(bind=engine)
        logger.info("📊 Tables de base de données créées")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt du service Orders API")

# Créer l'application FastAPI
app = FastAPI(
    title="📦 Orders API",
    description="Service de gestion des commandes et checkout",
    version="1.0.0",
    lifespan=lifespan
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
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    logger.info(f"🔍 [{request_id}] {request.method} {request.url.path} - Début")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"✅ [{request_id}] {request.method} {request.url.path} - "
                   f"Status: {response.status_code} - Temps: {process_time:.3f}s")
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ [{request_id}] {request.method} {request.url.path} - "
                    f"Erreur: {str(e)} - Temps: {process_time:.3f}s")
        raise

# Gestionnaire d'erreurs global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'erreurs HTTP personnalisé"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    if isinstance(exc.detail, dict):
        error_detail = exc.detail
    else:
        error_detail = {
            "error": "HTTP Exception",
            "message": exc.detail,
            "service": "orders-api"
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail,
        headers={"X-Request-ID": request_id}
    )

# Services métier
def generate_order_number() -> str:
    """Génère un numéro de commande unique"""
    timestamp = int(time.time())
    return f"ORD-{timestamp}"

async def get_cart_data(cart_id: int):
    """Récupère les données du panier depuis l'API Cart"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CART_API_URL}/api/v1/carts/{cart_id}")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error(f"❌ Erreur récupération panier {cart_id}: {str(e)}")
        return None

async def process_checkout(db: Session, checkout_data: schemas.CheckoutRequest) -> models.Order:
    """Traite une commande de checkout"""
    
    # 1. Récupérer le panier
    cart_data = await get_cart_data(checkout_data.cart_id)
    if not cart_data or not cart_data.get("items"):
        raise ValueError("Panier vide ou non trouvé")
    
    # 2. Calculer les montants
    subtotal = Decimal(str(cart_data["total_price"]))
    tax_rate = Decimal("0.20")  # 20% TVA
    tax_amount = subtotal * tax_rate
    shipping_amount = Decimal("5.00") if subtotal < 50 else Decimal("0.00")
    total_amount = subtotal + tax_amount + shipping_amount
    
    # 3. Créer la commande
    order = models.Order(
        order_number=generate_order_number(),
        customer_id=checkout_data.customer_id,
        cart_id=checkout_data.cart_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        shipping_address=checkout_data.shipping_address,
        billing_address=checkout_data.billing_address
    )
    
    db.add(order)
    db.flush()
    
    # 4. Créer les éléments de commande
    for cart_item in cart_data["items"]:
        # Récupérer le nom du produit
        product_name = f"Produit {cart_item['product_id']}"
        try:
            async with httpx.AsyncClient() as client:
                product_response = await client.get(f"{PRODUCTS_API_URL}/api/v1/products/{cart_item['product_id']}")
                if product_response.status_code == 200:
                    product_data = product_response.json()
                    product_name = product_data.get("nom", product_name)
        except:
            pass
        
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=cart_item["product_id"],
            product_name=product_name,
            quantity=cart_item["quantity"],
            unit_price=cart_item["unit_price"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    return order

# Routes de base
@app.get("/")
async def root():
    """🏠 Point d'entrée de l'API"""
    return {
        "service": "orders-api",
        "version": "1.0.0",
        "description": "Service de gestion des commandes",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """🏥 Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "orders-api",
        "timestamp": time.time()
    }

# Endpoints principaux
@app.post("/api/v1/orders/checkout", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    checkout_data: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🛒 Transformer un panier en commande (checkout)"""
    logger.info(f"🛒 Checkout panier {checkout_data.cart_id} pour client {checkout_data.customer_id} [Request-ID: {x_request_id}]")
    
    try:
        order = await process_checkout(db, checkout_data)
        logger.info(f"✅ Commande créée: {order.order_number} [Request-ID: {x_request_id}]")
        
        # Enrichir la réponse
        response = schemas.OrderResponse.from_orm(order)
        response.total_items = order.total_items
        response.items = [schemas.OrderItemResponse.from_orm(item) for item in order.items]
        
        return response
        
    except ValueError as e:
        logger.warning(f"⚠️ Erreur checkout: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Checkout failed",
                "message": str(e),
                "service": "orders-api"
            }
        )
    except Exception as e:
        logger.error(f"❌ Erreur checkout: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "Erreur lors du checkout",
                "service": "orders-api"
            }
        )

@app.get("/api/v1/orders", response_model=List[schemas.OrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None,
    status: Optional[schemas.OrderStatus] = None,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📋 Lister les commandes avec filtres"""
    logger.info(f"📋 Récupération commandes (skip={skip}, limit={limit}) [Request-ID: {x_request_id}]")
    
    query = db.query(models.Order)
    
    if customer_id:
        query = query.filter(models.Order.customer_id == customer_id)
    if status:
        query = query.filter(models.Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    
    response = []
    for order in orders:
        order_response = schemas.OrderResponse.from_orm(order)
        order_response.total_items = order.total_items
        order_response.items = [schemas.OrderItemResponse.from_orm(item) for item in order.items]
        response.append(order_response)
    
    return response

@app.get("/api/v1/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Récupérer une commande par ID"""
    logger.info(f"🔍 Récupération commande: {order_id} [Request-ID: {x_request_id}]")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Order not found",
                "message": "Commande non trouvée",
                "service": "orders-api"
            }
        )
    
    response = schemas.OrderResponse.from_orm(order)
    response.total_items = order.total_items
    response.items = [schemas.OrderItemResponse.from_orm(item) for item in order.items]
    
    return response

@app.put("/api/v1/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdateStatus,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """✏️ Mettre à jour le statut d'une commande"""
    logger.info(f"✏️ Mise à jour statut commande {order_id}: {status_update.status} [Request-ID: {x_request_id}]")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Order not found",
                "message": "Commande non trouvée",
                "service": "orders-api"
            }
        )
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    
    # Mettre à jour les timestamps spécifiques
    if status_update.status == schemas.OrderStatus.CONFIRMED:
        order.confirmed_at = datetime.utcnow()
    elif status_update.status == schemas.OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
    elif status_update.status == schemas.OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    response = schemas.OrderResponse.from_orm(order)
    response.total_items = order.total_items
    response.items = [schemas.OrderItemResponse.from_orm(item) for item in order.items]
    
    logger.info(f"✅ Statut commande {order_id} mis à jour [Request-ID: {x_request_id}]")
    return response

@app.get("/api/v1/orders/stats/summary", response_model=schemas.OrderStats)
def get_order_statistics(
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📊 Statistiques des commandes"""
    logger.info(f"📊 Récupération statistiques commandes [Request-ID: {x_request_id}]")
    
    total = db.query(func.count(models.Order.id)).scalar() or 0
    pending = db.query(func.count(models.Order.id)).filter(models.Order.status == models.OrderStatus.PENDING).scalar() or 0
    completed = db.query(func.count(models.Order.id)).filter(models.Order.status == models.OrderStatus.DELIVERED).scalar() or 0
    
    revenue = db.query(func.sum(models.Order.total_amount)).filter(
        models.Order.payment_status == models.PaymentStatus.PAID
    ).scalar() or Decimal('0.00')
    
    today = datetime.utcnow().date()
    orders_today = db.query(func.count(models.Order.id)).filter(
        func.date(models.Order.created_at) == today
    ).scalar() or 0
    
    return schemas.OrderStats(
        total_orders=total,
        pending_orders=pending,
        completed_orders=completed,
        total_revenue=Decimal(str(revenue)),
        orders_today=orders_today
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008) 