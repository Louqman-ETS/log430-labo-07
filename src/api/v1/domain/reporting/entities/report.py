from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class GlobalSummary:
    """
    Global Summary Entity - Aggregate sales data across all stores
    """

    total_revenue: Decimal
    total_sales_count: int
    average_ticket: Decimal

    def __post_init__(self):
        if self.total_revenue < 0:
            raise ValueError("Total revenue cannot be negative")
        if self.total_sales_count < 0:
            raise ValueError("Sales count cannot be negative")
        if self.average_ticket < 0:
            raise ValueError("Average ticket cannot be negative")

    @classmethod
    def calculate_from_data(
        cls, total_revenue: Decimal, total_sales_count: int
    ) -> "GlobalSummary":
        """Factory method to calculate global summary from raw data"""
        average_ticket = (
            total_revenue / total_sales_count
            if total_sales_count > 0
            else Decimal("0.00")
        )
        return cls(
            total_revenue=total_revenue,
            total_sales_count=total_sales_count,
            average_ticket=average_ticket,
        )


@dataclass
class StorePerformance:
    """
    Store Performance Entity - Performance metrics for a specific store
    """

    store_id: int
    store_name: str
    sales_count: int
    revenue: Decimal
    average_ticket: Decimal

    def __post_init__(self):
        if self.store_id <= 0:
            raise ValueError("Store ID must be positive")
        if not self.store_name:
            raise ValueError("Store name is required")
        if self.sales_count < 0:
            raise ValueError("Sales count cannot be negative")
        if self.revenue < 0:
            raise ValueError("Revenue cannot be negative")

    @classmethod
    def calculate_from_data(
        cls, store_id: int, store_name: str, sales_count: int, revenue: Decimal
    ) -> "StorePerformance":
        """Factory method to calculate store performance from raw data"""
        average_ticket = revenue / sales_count if sales_count > 0 else Decimal("0.00")
        return cls(
            store_id=store_id,
            store_name=store_name,
            sales_count=sales_count,
            revenue=revenue,
            average_ticket=average_ticket,
        )

    def performance_rating(self) -> str:
        """Business logic to rate store performance"""
        if self.revenue >= 10000:
            return "Excellent"
        elif self.revenue >= 5000:
            return "Good"
        elif self.revenue >= 1000:
            return "Average"
        else:
            return "Poor"


@dataclass
class TopProduct:
    """
    Top Product Entity - Product performance metrics
    """

    product_code: str
    product_name: str
    total_quantity_sold: int
    total_revenue: Decimal
    total_orders: int

    def __post_init__(self):
        if not self.product_code:
            raise ValueError("Product code is required")
        if not self.product_name:
            raise ValueError("Product name is required")
        if self.total_quantity_sold < 0:
            raise ValueError("Total quantity sold cannot be negative")
        if self.total_revenue < 0:
            raise ValueError("Total revenue cannot be negative")
        if self.total_orders < 0:
            raise ValueError("Total orders cannot be negative")

    def average_quantity_per_order(self) -> Decimal:
        """Calculate average quantity per order"""
        return (
            Decimal(self.total_quantity_sold) / self.total_orders
            if self.total_orders > 0
            else Decimal("0.00")
        )

    def average_revenue_per_order(self) -> Decimal:
        """Calculate average revenue per order"""
        return (
            self.total_revenue / self.total_orders
            if self.total_orders > 0
            else Decimal("0.00")
        )
