from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...schemas import SaleCreate, SaleResponse
from ...services import SaleService

router = APIRouter()

def get_sale_service(db: Session = Depends(get_db)) -> SaleService:
    return SaleService(db)

@router.get("/", response_model=List[SaleResponse])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    sale_service: SaleService = Depends(get_sale_service),
):
    """Retrieve sales with pagination."""
    return sale_service.get_sales(skip=skip, limit=limit)

@router.get("/{sale_id}", response_model=SaleResponse)
def read_sale(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service),
):
    """Get sale by ID."""
    sale = sale_service.get_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale with id {sale_id} not found")
    return sale

@router.post("/", response_model=SaleResponse, status_code=201)
async def create_sale(
    sale: SaleCreate,
    sale_service: SaleService = Depends(get_sale_service),
):
    """Create new sale."""
    try:
        return await sale_service.create_sale(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/store/{store_id}", response_model=List[SaleResponse])
def get_sales_by_store(
    store_id: int,
    sale_service: SaleService = Depends(get_sale_service),
):
    """Get all sales for a specific store."""
    return sale_service.get_sales_by_store(store_id) 