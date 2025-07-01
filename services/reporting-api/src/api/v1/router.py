from fastapi import APIRouter
from .reports import router as reports_router
from .sales import router as sales_router
from .stocks import router as stocks_router

api_router = APIRouter()

# Include routers
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(sales_router, prefix="/sales", tags=["sales"])
api_router.include_router(stocks_router, prefix="/stocks", tags=["stocks"]) 