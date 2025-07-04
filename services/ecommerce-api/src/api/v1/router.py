from fastapi import APIRouter
from .customers import router as customers_router
from .carts import router as carts_router
from .orders import router as orders_router

api_router = APIRouter()

# Inclure tous les routers avec leurs préfixes
api_router.include_router(customers_router, prefix="/customers", tags=["customers"])
api_router.include_router(carts_router, prefix="/carts", tags=["carts"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
