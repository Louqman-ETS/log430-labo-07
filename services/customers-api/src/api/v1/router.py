from fastapi import APIRouter
from .customers import router as customers_router
from .addresses import router as addresses_router

router = APIRouter()

# Inclure tous les routeurs avec leurs préfixes
router.include_router(customers_router, prefix="/customers", tags=["customers"])
router.include_router(addresses_router, prefix="/customers/me/addresses", tags=["addresses"]) 