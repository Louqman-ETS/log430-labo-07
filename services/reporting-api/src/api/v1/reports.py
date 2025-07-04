from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.services import ReportingService
from src.schemas import (
    GlobalSummaryResponse,
    StorePerformanceResponse,
    TopProductResponse,
)

logger = logging.getLogger("reporting-api")

router = APIRouter()


# Dependency to get database session (not needed for reporting API)
def get_db():
    return None


@router.get("/global-summary", response_model=GlobalSummaryResponse)
async def get_global_summary(db: Session = Depends(get_db)):
    """Get global business summary"""
    logger.info("📊 Global summary requested")
    service = ReportingService(db)
    return await service.get_global_summary()


@router.get("/store-performances", response_model=List[StorePerformanceResponse])
async def get_store_performances(db: Session = Depends(get_db)):
    """Get performance metrics for all stores"""
    logger.info("🏪 Store performances requested")
    service = ReportingService(db)
    return await service.get_store_performances()


@router.get("/top-stores", response_model=List[StorePerformanceResponse])
async def get_top_stores(
    limit: int = Query(5, ge=1, le=50, description="Number of top stores to return"),
    db: Session = Depends(get_db),
):
    """Get top performing stores"""
    logger.info(f"🏆 Top {limit} stores requested")
    service = ReportingService(db)
    performances = await service.get_store_performances()
    return performances[:limit]


@router.get("/underperforming-stores", response_model=List[StorePerformanceResponse])
async def get_underperforming_stores(
    threshold: float = Query(1000.0, ge=0, description="Revenue threshold"),
    db: Session = Depends(get_db),
):
    """Get stores with revenue below threshold"""
    logger.info(f"⚠️ Underperforming stores requested (threshold: {threshold})")
    service = ReportingService(db)
    performances = await service.get_store_performances()
    get_revenue = lambda p: p.revenue if hasattr(p, "revenue") else p["revenue"]
    return [p for p in performances if get_revenue(p) < threshold]


@router.get("/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    db: Session = Depends(get_db),
):
    """Get top performing products"""
    logger.info(f"📈 Top {limit} products requested")
    service = ReportingService(db)
    return await service.get_top_products(limit)


@router.get("/products-by-revenue", response_model=List[TopProductResponse])
async def get_products_by_revenue(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    db: Session = Depends(get_db),
):
    """Get products sorted by revenue"""
    logger.info(f"💰 Products by revenue requested (limit: {limit})")
    service = ReportingService(db)
    return await service.get_top_products(limit)


@router.get("/products-by-volume", response_model=List[TopProductResponse])
async def get_products_by_volume(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    db: Session = Depends(get_db),
):
    """Get products sorted by quantity sold"""
    logger.info(f"📦 Products by volume requested (limit: {limit})")
    service = ReportingService(db)
    products = await service.get_top_products(limit * 2)  # Get more to sort by volume
    get_qty = lambda x: (
        x.total_quantity_sold
        if hasattr(x, "total_quantity_sold")
        else x["total_quantity_sold"]
    )
    sorted_products = sorted(products, key=get_qty, reverse=True)
    return sorted_products[:limit]


@router.get("/store/{store_id}/performance", response_model=StorePerformanceResponse)
async def get_store_performance(store_id: int, db: Session = Depends(get_db)):
    """Get performance for a specific store"""
    logger.info(f"🏪 Store {store_id} performance requested")
    service = ReportingService(db)
    performance = await service.get_store_performance(store_id)
    if not performance:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")
    return performance


@router.get("/all-stores-performance", response_model=List[StorePerformanceResponse])
async def get_all_stores_performance(db: Session = Depends(get_db)):
    """Get performance for all stores (alias for store-performances)"""
    logger.info("🏪 All stores performance requested")
    service = ReportingService(db)
    return await service.get_store_performances()


@router.get("/business-insights")
async def get_business_insights(db: Session = Depends(get_db)):
    """Get business insights and recommendations"""
    logger.info("💡 Business insights requested")
    service = ReportingService(db)

    # Get data for insights
    summary = await service.get_global_summary()
    performances = await service.get_store_performances()
    top_products = await service.get_top_products(5)

    get_total_revenue = lambda s: (
        s.total_revenue if hasattr(s, "total_revenue") else s["total_revenue"]
    )
    get_total_stores = lambda s: (
        s.total_stores if hasattr(s, "total_stores") else s["total_stores"]
    )
    get_product_name = lambda p: (
        p.product_name if hasattr(p, "product_name") else p["product_name"]
    )

    insights = {
        "summary": summary,
        "insights": [
            {
                "type": "performance",
                "message": f"Total revenue: ${get_total_revenue(summary):.2f}",
                "recommendation": "Focus on high-performing stores for expansion",
            },
            {
                "type": "stores",
                "message": f"Active stores: {get_total_stores(summary)}",
                "recommendation": "Consider opening new locations in underserved areas",
            },
            {
                "type": "products",
                "message": f"Top product: {get_product_name(top_products[0]) if top_products else 'N/A'}",
                "recommendation": "Increase stock of best-selling products",
            },
        ],
        "top_performing_stores": (
            performances[:3] if len(performances) >= 3 else performances
        ),
        "top_products": top_products,
    }

    return insights


# Mock endpoints for additional reporting features
@router.get("/sales-by-period")
async def get_sales_by_period(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    db: Session = Depends(get_db),
):
    """Get sales data grouped by time period"""
    logger.info(f"📅 Sales by {period} requested")
    return {
        "period": period,
        "message": "This endpoint would provide sales data grouped by time period",
        "data": [],
    }


@router.get("/inventory-status")
async def get_inventory_status(db: Session = Depends(get_db)):
    """Get current inventory status across all stores"""
    logger.info("📦 Inventory status requested")
    return {
        "message": "This endpoint would provide current inventory levels",
        "low_stock_items": [],
        "out_of_stock_items": [],
    }


@router.get("/revenue-trends")
async def get_revenue_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """Get revenue trends over time"""
    logger.info(f"📈 Revenue trends requested (last {days} days)")
    return {
        "period_days": days,
        "message": "This endpoint would provide revenue trends over time",
        "trends": [],
    }
