from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ...database import get_db
from ...schemas import (
    GlobalSummaryResponse, StorePerformanceResponse, TopProductResponse,
    SalesReportResponse
)
from ...services import ReportingService

router = APIRouter()

def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    return ReportingService(db)

@router.get("/global-summary", response_model=GlobalSummaryResponse)
async def get_global_summary(
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get global business summary using data from all services"""
    try:
        return await reporting_service.get_global_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate global summary: {str(e)}")

@router.get("/store-performances", response_model=List[StorePerformanceResponse])
async def get_store_performances(
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get performance metrics for all stores"""
    try:
        return await reporting_service.get_store_performances()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-stores", response_model=List[StorePerformanceResponse])
async def get_top_performing_stores(
    limit: int = Query(5, ge=1, le=20, description="Number of top stores to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get top performing stores"""
    try:
        performances = await reporting_service.get_store_performances()
        return performances[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/underperforming-stores", response_model=List[StorePerformanceResponse])
async def get_underperforming_stores(
    threshold: float = Query(1000.0, ge=0, description="Revenue threshold for underperforming stores"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get stores that need attention"""
    try:
        performances = await reporting_service.get_store_performances()
        return [p for p in performances if p.revenue < threshold]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Number of top products to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get top performing products"""
    try:
        return await reporting_service.get_top_products(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate top products report: {str(e)}")

@router.get("/products-by-revenue", response_model=List[TopProductResponse])
async def get_products_by_revenue(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get products ranked by revenue"""
    try:
        return await reporting_service.get_top_products(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products-by-volume", response_model=List[TopProductResponse])
async def get_products_by_volume(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get products ranked by quantity sold"""
    try:
        products = await reporting_service.get_top_products(100)  # Get more to sort
        # Sort by quantity sold
        sorted_products = sorted(products, key=lambda x: x.total_quantity_sold, reverse=True)
        return sorted_products[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/performance", response_model=StorePerformanceResponse)
async def get_store_performance(
    store_id: int,
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get performance metrics for a specific store."""
    try:
        performance = await reporting_service.get_store_performance(store_id)
        if not performance:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return performance
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stores/performance", response_model=List[StorePerformanceResponse])
async def get_all_stores_performance(
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of stores to return"),
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get performance for all stores"""
    try:
        performances = await reporting_service.get_store_performances()
        return performances[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business-insights")
async def get_business_insights(
    reporting_service: ReportingService = Depends(get_reporting_service),
):
    """Get comprehensive business insights"""
    try:
        summary = await reporting_service.get_global_summary()
        performances = await reporting_service.get_store_performances()

        # Calculate business insights
        total_stores = len(performances)
        active_stores = len([p for p in performances if p.sales_count > 0])
        best_store = max(performances, key=lambda x: x.revenue) if performances else None

        insights = {
            "global_summary": summary,
            "total_stores": total_stores,
            "active_stores": active_stores,
            "store_activation_rate": (active_stores / total_stores * 100) if total_stores > 0 else 0,
            "best_performing_store": best_store,
            "average_store_revenue": (sum(p.revenue for p in performances) / len(performances)) if performances else 0,
        }

        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mock endpoints for compatibility
@router.get("/sales-by-period", response_model=SalesReportResponse)
async def get_sales_by_period(
    period: str = Query(..., pattern="^(daily|weekly|monthly)$", description="Period: daily, weekly, or monthly"),
    start_date: Optional[date] = Query(default=None, description="Start date for the report"),
    end_date: Optional[date] = Query(default=None, description="End date for the report"),
    store_id: Optional[int] = Query(default=None, description="Filter by specific store"),
):
    """Get sales aggregated by time period (mock implementation)"""
    return SalesReportResponse(
        period=period,
        start_date=start_date or date.today(),
        end_date=end_date or date.today(),
        store_id=store_id,
        total_sales=0,
        total_revenue=0,
        sales_data=[],
    )

@router.get("/inventory-status", response_model=dict)
async def get_inventory_status(
    low_stock_threshold: int = Query(default=10, ge=0, description="Threshold for low stock alert"),
    store_id: Optional[int] = Query(default=None, description="Filter by specific store"),
):
    """Get current inventory status (mock implementation)"""
    return {
        "low_stock_threshold": low_stock_threshold,
        "store_id": store_id,
        "low_stock_products": [],
        "out_of_stock_products": [],
        "total_products": 0,
        "inventory_value": 0,
    }

@router.get("/revenue-trends", response_model=dict)
async def get_revenue_trends(
    period: str = Query(default="monthly", pattern="^(daily|weekly|monthly)$", description="Period for trend analysis"),
    months_back: int = Query(default=12, ge=1, le=36, description="Number of months to look back"),
    store_id: Optional[int] = Query(default=None, description="Filter by specific store"),
):
    """Get revenue trends over time (mock implementation)"""
    return {
        "period": period,
        "months_back": months_back,
        "store_id": store_id,
        "trends": [],
        "growth_rate": 0,
        "trend_direction": "stable",
    } 