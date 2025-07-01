from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...services import SaleService
from ... import schemas

router = APIRouter()

def get_sale_service(db: Session = Depends(get_db)) -> SaleService:
    return SaleService(db)

@router.post("/", response_model=schemas.SaleResponse)
async def create_sale(
    sale: schemas.SaleCreate,
    service: SaleService = Depends(get_sale_service)
):
    """Créer une nouvelle vente"""
    try:
        return await service.create_sale(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sale: {str(e)}")

@router.get("/", response_model=List[schemas.SaleResponse])
def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SaleService = Depends(get_sale_service)
):
    """Récupérer toutes les ventes"""
    return service.get_sales(skip=skip, limit=limit)

@router.get("/stats", response_model=schemas.SalesStats)
def get_sales_stats(service: SaleService = Depends(get_sale_service)):
    """Récupérer les statistiques des ventes"""
    return service.get_sales_stats()

@router.get("/store/{store_id}", response_model=List[schemas.SaleResponse])
def get_sales_by_store(
    store_id: int,
    service: SaleService = Depends(get_sale_service)
):
    """Récupérer les ventes d'un magasin"""
    return service.get_sales_by_store(store_id)

@router.get("/product/{product_id}", response_model=List[schemas.SaleResponse])
def get_sales_by_product(
    product_id: int,
    service: SaleService = Depends(get_sale_service)
):
    """Récupérer les ventes contenant un produit"""
    return service.get_sales_by_product(product_id)

@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(
    sale_id: int,
    service: SaleService = Depends(get_sale_service)
):
    """Récupérer une vente par ID"""
    sale = service.get_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale 