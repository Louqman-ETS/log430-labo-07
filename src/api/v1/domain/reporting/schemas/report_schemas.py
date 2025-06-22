from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date


class GlobalSummaryResponse(BaseModel):
    """Schema for global summary response"""

    model_config = ConfigDict(from_attributes=True)

    total_revenue: Decimal
    total_sales_count: int
    average_ticket: Decimal


class StorePerformanceResponse(BaseModel):
    """Schema for store performance response"""

    model_config = ConfigDict(from_attributes=True)

    store_id: int
    store_name: str
    sales_count: int
    revenue: Decimal
    average_ticket: Decimal
    performance_rating: str


class TopProductResponse(BaseModel):
    """Schema for top product response"""

    model_config = ConfigDict(from_attributes=True)

    product_code: str
    product_name: str
    total_quantity_sold: int
    total_revenue: Decimal
    total_orders: int
    average_quantity_per_order: Decimal
    average_revenue_per_order: Decimal


class SalesReportResponse(BaseModel):
    """Schema for sales report response"""

    model_config = ConfigDict(from_attributes=True)

    period: str
    start_date: date
    end_date: date
    store_id: Optional[int] = None
    total_sales: int
    total_revenue: Decimal
    sales_data: List[Dict[str, Any]]
