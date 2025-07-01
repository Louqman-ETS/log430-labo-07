from fastapi import APIRouter
from .stores import router as stores_router
from .cash_registers import router as cash_registers_router

api_router = APIRouter()

# Include routers
api_router.include_router(stores_router, prefix="/stores", tags=["stores"])
api_router.include_router(cash_registers_router, prefix="/cash-registers", tags=["cash-registers"]) 