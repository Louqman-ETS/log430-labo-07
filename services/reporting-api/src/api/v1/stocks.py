from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...schemas import (
    StoreStockCreate, StoreStockResponse, CentralStockCreate, CentralStockResponse,
    RestockingRequestCreate, RestockingRequestResponse
)
from ...services import StockService, RestockingService

router = APIRouter()

def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    return StockService(db)

def get_restocking_service(db: Session = Depends(get_db)) -> RestockingService:
    return RestockingService(db)

# Store stocks endpoints
@router.get("/store/{store_id}", response_model=List[StoreStockResponse])
def get_store_stocks(
    store_id: int,
    stock_service: StockService = Depends(get_stock_service),
):
    """Get all stock entries for a specific store."""
    return stock_service.get_store_stocks(store_id)

@router.post("/store", response_model=StoreStockResponse, status_code=201)
async def create_store_stock(
    stock: StoreStockCreate,
    stock_service: StockService = Depends(get_stock_service),
):
    """Create new store stock entry."""
    try:
        return await stock_service.create_store_stock(stock)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Central stocks endpoints
@router.get("/central", response_model=List[CentralStockResponse])
def get_central_stocks(
    stock_service: StockService = Depends(get_stock_service),
):
    """Get all central stock entries."""
    return stock_service.get_central_stocks()

@router.get("/central/{product_id}", response_model=CentralStockResponse)
def get_central_stock(
    product_id: int,
    stock_service: StockService = Depends(get_stock_service),
):
    """Get central stock for a specific product."""
    stock = stock_service.get_central_stock(product_id)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Central stock for product {product_id} not found")
    return stock

@router.post("/central", response_model=CentralStockResponse, status_code=201)
async def create_central_stock(
    stock: CentralStockCreate,
    stock_service: StockService = Depends(get_stock_service),
):
    """Create new central stock entry."""
    try:
        return await stock_service.create_central_stock(stock)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Restocking requests endpoints
@router.get("/restocking-requests", response_model=List[RestockingRequestResponse])
def get_restocking_requests(
    restocking_service: RestockingService = Depends(get_restocking_service),
):
    """Get all restocking requests."""
    return restocking_service.get_restocking_requests()

@router.get("/restocking-requests/{request_id}", response_model=RestockingRequestResponse)
def get_restocking_request(
    request_id: int,
    restocking_service: RestockingService = Depends(get_restocking_service),
):
    """Get restocking request by ID."""
    request = restocking_service.get_restocking_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Restocking request with id {request_id} not found")
    return request

@router.get("/restocking-requests/store/{store_id}", response_model=List[RestockingRequestResponse])
def get_restocking_requests_by_store(
    store_id: int,
    restocking_service: RestockingService = Depends(get_restocking_service),
):
    """Get all restocking requests for a specific store."""
    return restocking_service.get_restocking_requests_by_store(store_id)

@router.post("/restocking-requests", response_model=RestockingRequestResponse, status_code=201)
async def create_restocking_request(
    request: RestockingRequestCreate,
    restocking_service: RestockingService = Depends(get_restocking_service),
):
    """Create new restocking request."""
    try:
        return await restocking_service.create_restocking_request(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/restocking-requests/{request_id}/status")
async def update_restocking_request_status(
    request_id: int,
    status: str,
    restocking_service: RestockingService = Depends(get_restocking_service),
):
    """Update restocking request status."""
    try:
        updated_request = restocking_service.update_restocking_request_status(request_id, status)
        if not updated_request:
            raise HTTPException(status_code=404, detail=f"Restocking request with id {request_id} not found")
        return updated_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 