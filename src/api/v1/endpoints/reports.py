from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from src.db import get_db
from ..dependencies import api_token_auth
from ..errors import NotFoundError, BusinessLogicError
from ..domain.reporting.entities.report import (
    GlobalSummary,
    StorePerformance,
    TopProduct,
)
from ..domain.reporting.repositories.reporting_repository import ReportingRepository
from ..domain.reporting.services.reporting_service import ReportingService
from ..domain.reporting.schemas.report_schemas import (
    GlobalSummaryResponse,
    StorePerformanceResponse,
    TopProductResponse,
    SalesReportResponse,
)

router = APIRouter()


def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    """Dependency injection for ReportingService"""
    reporting_repository = ReportingRepository(db)
    return ReportingService(reporting_repository)


@router.get("/global-summary", response_model=GlobalSummaryResponse)
async def get_global_summary(
    start_date: Optional[date] = Query(
        default=None, description="Start date for the report"
    ),
    end_date: Optional[date] = Query(
        default=None, description="End date for the report"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get global business summary using DDD architecture
    """
    try:
        summary = reporting_service.get_global_summary(start_date, end_date)
        return summary
    except Exception as e:
        raise BusinessLogicError(f"Failed to generate global summary: {str(e)}")


@router.get("/store-performances", response_model=List[StorePerformanceResponse])
def get_store_performances(
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get performance metrics for all stores using DDD architecture
    """
    try:
        return reporting_service.get_store_performances()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-stores", response_model=List[StorePerformanceResponse])
def get_top_performing_stores(
    limit: int = Query(5, ge=1, le=20, description="Number of top stores to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get top performing stores - Business query using DDD
    """
    try:
        return reporting_service.get_top_performing_stores(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/underperforming-stores", response_model=List[StorePerformanceResponse])
def get_underperforming_stores(
    threshold: float = Query(
        1000.0, ge=0, description="Revenue threshold for underperforming stores"
    ),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get stores that need attention - Business logic using DDD
    """
    try:
        return reporting_service.get_underperforming_stores(threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    limit: int = Query(
        default=10, ge=1, le=50, description="Number of top products to return"
    ),
    start_date: Optional[date] = Query(
        default=None, description="Start date for the report"
    ),
    end_date: Optional[date] = Query(
        default=None, description="End date for the report"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get top performing products using DDD architecture
    """
    try:
        top_products = reporting_service.get_top_products(limit, start_date, end_date)
        return top_products
    except Exception as e:
        raise BusinessLogicError(f"Failed to generate top products report: {str(e)}")


@router.get("/products-by-revenue", response_model=List[TopProductResponse])
def get_products_by_revenue(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get products ranked by revenue - Business query using DDD
    """
    try:
        return reporting_service.get_products_by_revenue(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products-by-volume", response_model=List[TopProductResponse])
def get_products_by_volume(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get products ranked by quantity sold - Business query using DDD
    """
    try:
        return reporting_service.get_products_by_volume(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-insights")
def get_business_insights(
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """
    Get comprehensive business insights - Advanced business analysis using DDD
    """
    try:
        return reporting_service.get_business_insights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/{store_id}/performance", response_model=StorePerformanceResponse)
async def get_store_performance(
    store_id: int,
    start_date: Optional[date] = Query(
        default=None, description="Start date for the report"
    ),
    end_date: Optional[date] = Query(
        default=None, description="End date for the report"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get performance metrics for a specific store."""
    try:
        performance = reporting_service.get_store_performance(
            store_id, start_date, end_date
        )
        if not performance:
            raise NotFoundError("Store performance data", store_id)
        return performance
    except ValueError as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Store", store_id)
        raise BusinessLogicError(str(e))


@router.get("/stores/performance", response_model=List[StorePerformanceResponse])
async def get_all_stores_performance(
    start_date: Optional[date] = Query(
        default=None, description="Start date for the report"
    ),
    end_date: Optional[date] = Query(
        default=None, description="End date for the report"
    ),
    limit: int = Query(
        default=10, ge=1, le=50, description="Maximum number of stores to return"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get performance metrics for all stores, sorted by revenue."""
    try:
        performances = reporting_service.get_all_stores_performance(
            start_date, end_date, limit
        )
        return performances
    except Exception as e:
        raise BusinessLogicError(
            f"Failed to generate stores performance report: {str(e)}"
        )


@router.get("/sales-by-period", response_model=SalesReportResponse)
async def get_sales_by_period(
    period: str = Query(
        ...,
        pattern="^(daily|weekly|monthly)$",
        description="Period: daily, weekly, or monthly",
    ),
    start_date: Optional[date] = Query(
        default=None, description="Start date for the report"
    ),
    end_date: Optional[date] = Query(
        default=None, description="End date for the report"
    ),
    store_id: Optional[int] = Query(
        default=None, description="Filter by specific store"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get sales aggregated by time period (daily, weekly, monthly)."""
    try:
        sales_report = reporting_service.get_sales_by_period(
            period, start_date, end_date, store_id
        )
        return sales_report
    except ValueError as e:
        if "store" in str(e).lower() and "not found" in str(e).lower():
            raise NotFoundError("Store", store_id)
        raise BusinessLogicError(str(e))
    except Exception as e:
        raise BusinessLogicError(f"Failed to generate sales report: {str(e)}")


@router.get("/inventory-status", response_model=dict)
async def get_inventory_status(
    low_stock_threshold: int = Query(
        default=10, ge=0, description="Threshold for low stock alert"
    ),
    store_id: Optional[int] = Query(
        default=None, description="Filter by specific store"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get current inventory status with low stock alerts."""
    try:
        inventory_status = reporting_service.get_inventory_status(
            low_stock_threshold, store_id
        )
        return inventory_status
    except ValueError as e:
        if "store" in str(e).lower() and "not found" in str(e).lower():
            raise NotFoundError("Store", store_id)
        raise BusinessLogicError(str(e))
    except Exception as e:
        raise BusinessLogicError(f"Failed to generate inventory status: {str(e)}")


@router.get("/revenue-trends", response_model=dict)
async def get_revenue_trends(
    period: str = Query(
        default="monthly",
        pattern="^(daily|weekly|monthly)$",
        description="Period for trend analysis",
    ),
    months_back: int = Query(
        default=12, ge=1, le=36, description="Number of months to look back"
    ),
    store_id: Optional[int] = Query(
        default=None, description="Filter by specific store"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get revenue trends over time with growth analysis."""
    try:
        trends = reporting_service.get_revenue_trends(period, months_back, store_id)
        return trends
    except ValueError as e:
        if "store" in str(e).lower() and "not found" in str(e).lower():
            raise NotFoundError("Store", store_id)
        raise BusinessLogicError(str(e))
    except Exception as e:
        raise BusinessLogicError(f"Failed to generate revenue trends: {str(e)}")
