from fastapi import APIRouter

from src.api.v1.endpoints import products, stores, reports

api_router = APIRouter()

# DDD-based endpoints (now the main endpoints)
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
