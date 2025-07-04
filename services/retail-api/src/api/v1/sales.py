from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.models as models
import src.schemas as schemas
from src.services import SaleService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.SaleResponse])
async def get_sales(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    cash_register_id: Optional[int] = Query(
        None, description="Filter by cash register ID"
    ),
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des ventes avec filtres"""
    logger.info(
        f"💰 Getting sales - store_id={store_id}, cash_register_id={cash_register_id}"
    )

    service = SaleService(db)
    return service.get_sales(
        store_id=store_id,
        cash_register_id=cash_register_id,
        date_debut=date_debut,
        date_fin=date_fin,
    )


@router.post("/", response_model=schemas.SaleResponse, status_code=201)
async def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle vente"""
    logger.info(f"➕ Creating sale for store {sale.store_id}")

    service = SaleService(db)
    return await service.create_sale(sale)


@router.get("/{sale_id}", response_model=schemas.SaleResponse)
async def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Récupérer une vente par son ID"""
    logger.info(f"💰 Getting sale {sale_id}")

    service = SaleService(db)
    sale = service.get_sale(sale_id)

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return sale


@router.put("/{sale_id}", response_model=schemas.SaleResponse)
async def update_sale(
    sale_id: int, sale_update: schemas.SaleUpdate, db: Session = Depends(get_db)
):
    """Mettre à jour une vente"""
    logger.info(f"✏️ Updating sale {sale_id}")

    service = SaleService(db)
    sale = service.update_sale(sale_id, sale_update)

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return sale


@router.delete("/{sale_id}", status_code=204)
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    """Supprimer une vente (annulation)"""
    logger.info(f"🗑️ Deleting sale {sale_id}")

    service = SaleService(db)
    success = service.delete_sale(sale_id)

    if not success:
        raise HTTPException(status_code=404, detail="Sale not found")


@router.get("/{sale_id}/lines", response_model=List[schemas.SaleLineResponse])
async def get_sale_lines(sale_id: int, db: Session = Depends(get_db)):
    """Récupérer les lignes d'une vente"""
    logger.info(f"💰 Getting sale lines for sale {sale_id}")

    service = SaleService(db)
    lines = service.get_sale_lines(sale_id)

    if not lines:
        raise HTTPException(status_code=404, detail="Sale not found")

    return lines


@router.get("/stats/summary", response_model=schemas.RetailSummary)
async def get_sales_summary(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    date_debut: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Obtenir un résumé des ventes"""
    logger.info(f"📊 Getting sales summary - store_id={store_id}")

    service = SaleService(db)
    return service.get_sales_summary(
        store_id=store_id, date_debut=date_debut, date_fin=date_fin
    )


@router.get("/stats/by-store")
async def get_sales_by_store(db: Session = Depends(get_db)):
    """Obtenir les ventes groupées par magasin"""
    logger.info("📊 Getting sales by store")

    service = SaleService(db)
    return service.get_sales_by_store()


@router.get("/stats/by-date")
async def get_sales_by_date(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    db: Session = Depends(get_db),
):
    """Obtenir les ventes groupées par date"""
    logger.info(f"📊 Getting sales by date - start={start_date}, end={end_date}")

    service = SaleService(db)
    return service.get_sales_by_date(
        start_date=start_date, end_date=end_date, store_id=store_id
    )
