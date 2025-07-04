from fastapi import APIRouter
from src.api.v1.reports import router as reports_router

api_router = APIRouter()

# Include routers
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
