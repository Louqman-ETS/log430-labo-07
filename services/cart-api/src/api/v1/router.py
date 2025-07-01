from fastapi import APIRouter
from .carts import router as carts_router

router = APIRouter()

# Inclure tous les routeurs avec leurs préfixes
router.include_router(carts_router, prefix="/carts", tags=["carts"]) 