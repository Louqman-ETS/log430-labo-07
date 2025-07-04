from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.models as models
import src.schemas as schemas
from src.services import ProductService, StockService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=schemas.ProductPage)
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(
        None, description="Search term for product name or code"
    ),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    actif: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des produits avec pagination et filtres"""
    logger.info(f"📋 Getting products - skip={skip}, limit={limit}, search={search}")

    service = ProductService(db)
    products, total = service.get_products(
        skip=skip, limit=limit, search=search, category_id=category_id, actif=actif
    )

    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1

    return schemas.ProductPage(
        items=products, total=total, page=current_page, size=limit, pages=pages
    )


@router.post("/", response_model=schemas.ProductResponse, status_code=201)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Créer un nouveau produit"""
    logger.info(f"➕ Creating product: {product.nom}")

    service = ProductService(db)
    return service.create_product(product)


@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Récupérer un produit par son ID"""
    logger.info(f"📋 Getting product {product_id}")

    service = ProductService(db)
    product = service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    """Mettre à jour un produit"""
    logger.info(f"✏️ Updating product {product_id}")

    service = ProductService(db)
    product = service.update_product(product_id, product_update)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Supprimer un produit (désactivation logique)"""
    logger.info(f"🗑️ Deleting product {product_id}")

    service = ProductService(db)
    success = service.delete_product(product_id)

    if not success:
        raise HTTPException(status_code=404, detail="Product not found")


# Stock management endpoints
@router.get("/{product_id}/stock", response_model=schemas.StockInfo)
async def get_product_stock(product_id: int, db: Session = Depends(get_db)):
    """Obtenir les informations de stock d'un produit"""
    logger.info(f"📦 Getting stock info for product {product_id}")

    service = StockService(db)
    stock_info = service.get_stock_info(product_id)

    if not stock_info:
        raise HTTPException(status_code=404, detail="Product not found")

    return stock_info


@router.put("/{product_id}/stock/adjust", response_model=schemas.ProductResponse)
async def adjust_product_stock(
    product_id: int, adjustment: schemas.StockAdjustment, db: Session = Depends(get_db)
):
    """Ajuster le stock d'un produit"""
    logger.info(f"📦 Adjusting stock for product {product_id} by {adjustment.quantite}")

    service = StockService(db)
    product = service.adjust_stock(product_id, adjustment)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/{product_id}/stock/status", response_model=schemas.ProductStockStatus)
async def get_product_stock_status(product_id: int, db: Session = Depends(get_db)):
    """Obtenir le statut complet du stock d'un produit avec les derniers mouvements"""
    logger.info(f"📦 Getting complete stock status for product {product_id}")

    service = StockService(db)
    status = service.get_stock_status(product_id)

    if not status:
        raise HTTPException(status_code=404, detail="Product not found")

    return status
