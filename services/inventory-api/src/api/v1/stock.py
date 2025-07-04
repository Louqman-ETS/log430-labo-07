from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.schemas as schemas
from src.services import StockService

logger = logging.getLogger(__name__)

router = APIRouter()


# Stock movements endpoints
@router.get("/movements", response_model=List[schemas.StockMovementResponse])
async def get_stock_movements(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    type_mouvement: Optional[str] = Query(None, description="Filter by movement type"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    db: Session = Depends(get_db),
):
    """Récupérer les mouvements de stock"""
    logger.info(
        f"📦 Getting stock movements - product_id={product_id}, type={type_mouvement}"
    )

    service = StockService(db)
    return service.get_stock_movements(
        product_id=product_id, type_mouvement=type_mouvement, limit=limit
    )


@router.post(
    "/movements", response_model=schemas.StockMovementResponse, status_code=201
)
async def create_stock_movement(
    movement: schemas.StockMovementCreate, db: Session = Depends(get_db)
):
    """Créer un nouveau mouvement de stock"""
    logger.info(f"📦 Creating stock movement for product {movement.product_id}")

    service = StockService(db)
    return service.create_stock_movement(movement)


# Stock alerts endpoints
@router.get("/alerts", response_model=List[schemas.StockAlertResponse])
async def get_stock_alerts(
    resolu: Optional[bool] = Query(None, description="Filter by resolved status"),
    type_alerte: Optional[str] = Query(None, description="Filter by alert type"),
    db: Session = Depends(get_db),
):
    """Récupérer les alertes de stock"""
    logger.info(f"⚠️ Getting stock alerts - resolu={resolu}, type={type_alerte}")

    service = StockService(db)
    return service.get_stock_alerts(resolu=resolu, type_alerte=type_alerte)


@router.put("/alerts/{alert_id}", response_model=schemas.StockAlertResponse)
async def update_stock_alert(
    alert_id: int, alert_update: schemas.StockAlertUpdate, db: Session = Depends(get_db)
):
    """Mettre à jour une alerte de stock"""
    logger.info(f"⚠️ Updating stock alert {alert_id}")

    service = StockService(db)
    alert = service.update_stock_alert(alert_id, alert_update)

    if not alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")

    return alert


# Inventory management endpoints
@router.get("/summary", response_model=schemas.InventorySummary)
async def get_inventory_summary(db: Session = Depends(get_db)):
    """Obtenir un résumé de l'inventaire"""
    logger.info("📊 Getting inventory summary")

    service = StockService(db)
    return service.get_inventory_summary()


@router.put("/products/{product_id}/stock/reduce")
async def reduce_stock(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Quantity to reduce"),
    raison: str = Query("vente", description="Reason for stock reduction"),
    reference: Optional[str] = Query(None, description="External reference"),
    db: Session = Depends(get_db),
):
    """Réduire le stock d'un produit (appelé lors d'une vente)"""
    logger.info(f"📦 Reducing stock for product {product_id} by {quantity}")

    service = StockService(db)
    result = service.reduce_stock(product_id, quantity, raison, reference)

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return result


@router.put("/products/{product_id}/stock/increase")
async def increase_stock(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Quantity to increase"),
    raison: str = Query("reapprovisionnement", description="Reason for stock increase"),
    reference: Optional[str] = Query(None, description="External reference"),
    db: Session = Depends(get_db),
):
    """Augmenter le stock d'un produit (réapprovisionnement)"""
    logger.info(f"📦 Increasing stock for product {product_id} by {quantity}")

    service = StockService(db)
    result = service.increase_stock(product_id, quantity, raison, reference)

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return result


@router.get("/products/{product_id}/stock")
async def get_stock(product_id: int, db: Session = Depends(get_db)):
    """Obtenir le niveau de stock d'un produit"""
    logger.info(f"📦 Getting stock level for product {product_id}")

    service = StockService(db)
    stock_info = service.get_stock_info(product_id)

    if not stock_info:
        raise HTTPException(status_code=404, detail="Product not found")

    return stock_info
