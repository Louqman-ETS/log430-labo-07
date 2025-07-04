from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Report schemas
class GlobalSummaryResponse(BaseModel):
    total_sales: int
    total_revenue: float
    total_products: int
    total_stores: int
    average_sale_amount: float


class StorePerformanceResponse(BaseModel):
    store_id: int
    store_name: Optional[str] = None
    sales_count: int
    revenue: float
    average_sale_amount: float
    performance_rating: str


class TopProductResponse(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    total_quantity_sold: int
    total_revenue: float
    sales_count: int


class SalesReportResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    store_id: Optional[int]
    total_sales: int
    total_revenue: float
    sales_data: List[dict]
