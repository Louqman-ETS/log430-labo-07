from pydantic import BaseModel
from decimal import Decimal
from typing import List, Dict, Any
from datetime import date


class GlobalSummaryResponse(BaseModel):
    """Schema for global summary response"""

    total_revenue: Decimal
    total_sales_count: int
    average_ticket: Decimal

    class Config:
        orm_mode = True


class StorePerformanceResponse(BaseModel):
    """Schema for store performance response"""

    store_id: int
    store_name: str
    sales_count: int
    revenue: Decimal
    average_ticket: Decimal
    performance_rating: str

    class Config:
        orm_mode = True


class TopProductResponse(BaseModel):
    """Schema for top product response"""

    product_code: str
    product_name: str
    total_quantity_sold: int
    total_revenue: Decimal
    total_orders: int
    average_quantity_per_order: Decimal
    average_revenue_per_order: Decimal

    class Config:
        orm_mode = True


class SalesReportResponse(BaseModel):
    """Schema for sales report response"""

    period: str
    start_date: date
    end_date: date
    store_id: int = None
    total_sales: int
    total_revenue: Decimal
    sales_data: List[Dict[str, Any]]

    class Config:
        orm_mode = True
