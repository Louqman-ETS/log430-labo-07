from typing import List, Optional
from datetime import date
from ..entities.report import GlobalSummary, StorePerformance, TopProduct
from ..repositories.reporting_repository import ReportingRepositoryInterface
from ..schemas.report_schemas import (
    GlobalSummaryResponse,
    StorePerformanceResponse,
    TopProductResponse,
    SalesReportResponse,
)


class ReportingService:
    """Application service for Reporting domain operations"""

    def __init__(self, reporting_repository: ReportingRepositoryInterface):
        self.reporting_repository = reporting_repository

    def get_global_summary(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> GlobalSummaryResponse:
        """Get global business summary"""
        summary = self.reporting_repository.get_global_summary()
        return self._global_summary_to_response(summary)

    def get_store_performance(
        self,
        store_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[StorePerformanceResponse]:
        """Get performance for a specific store"""
        performances = self.reporting_repository.get_store_performances()
        store_performance = next(
            (p for p in performances if p.store_id == store_id), None
        )
        if store_performance:
            return self._store_performance_to_response(store_performance)
        return None

    def get_all_stores_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
    ) -> List[StorePerformanceResponse]:
        """Get performance for all stores"""
        performances = self.reporting_repository.get_store_performances()
        # Sort by revenue descending and limit
        sorted_performances = sorted(
            performances, key=lambda x: x.revenue, reverse=True
        )[:limit]
        return [
            self._store_performance_to_response(performance)
            for performance in sorted_performances
        ]

    def get_store_performances(self) -> List[StorePerformanceResponse]:
        """Get all store performances with business ratings"""
        performances = self.reporting_repository.get_store_performances()
        return [
            self._store_performance_to_response(performance)
            for performance in performances
        ]

    def get_top_performing_stores(
        self, limit: int = 5
    ) -> List[StorePerformanceResponse]:
        """Get top performing stores - Business query"""
        all_performances = self.reporting_repository.get_store_performances()
        # Sort by revenue descending
        sorted_performances = sorted(
            all_performances, key=lambda x: x.revenue, reverse=True
        )
        top_performances = sorted_performances[:limit]
        return [
            self._store_performance_to_response(performance)
            for performance in top_performances
        ]

    def get_underperforming_stores(
        self, threshold_revenue: float = 1000.0
    ) -> List[StorePerformanceResponse]:
        """Get stores that need attention - Business logic"""
        all_performances = self.reporting_repository.get_store_performances()
        underperforming = [
            p for p in all_performances if float(p.revenue) < threshold_revenue
        ]
        return [
            self._store_performance_to_response(performance)
            for performance in underperforming
        ]

    def get_top_products(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[TopProductResponse]:
        """Get top performing products"""
        top_products = self.reporting_repository.get_top_products(limit)
        return [self._top_product_to_response(product) for product in top_products]

    def get_products_by_revenue(self, limit: int = 10) -> List[TopProductResponse]:
        """Get products ranked by revenue - Business query"""
        products = self.reporting_repository.get_top_products(limit)
        # Already sorted by revenue in repository
        return [self._top_product_to_response(product) for product in products]

    def get_products_by_volume(self, limit: int = 10) -> List[TopProductResponse]:
        """Get products ranked by quantity sold - Business query"""
        products = self.reporting_repository.get_top_products(100)  # Get more to sort
        # Sort by quantity sold
        sorted_products = sorted(
            products, key=lambda x: x.total_quantity_sold, reverse=True
        )
        return [
            self._top_product_to_response(product)
            for product in sorted_products[:limit]
        ]

    def get_sales_by_period(
        self,
        period: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
    ) -> SalesReportResponse:
        """Get sales aggregated by time period"""
        # For now, return a mock response - would need real implementation
        from datetime import datetime

        return SalesReportResponse(
            period=period,
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            store_id=store_id,
            total_sales=0,
            total_revenue=0,
            sales_data=[],
        )

    def get_inventory_status(
        self, low_stock_threshold: int = 10, store_id: Optional[int] = None
    ) -> dict:
        """Get current inventory status"""
        return {
            "low_stock_threshold": low_stock_threshold,
            "store_id": store_id,
            "low_stock_products": [],
            "out_of_stock_products": [],
            "total_products": 0,
            "inventory_value": 0,
        }

    def get_revenue_trends(
        self,
        period: str = "monthly",
        months_back: int = 12,
        store_id: Optional[int] = None,
    ) -> dict:
        """Get revenue trends over time"""
        return {
            "period": period,
            "months_back": months_back,
            "store_id": store_id,
            "trends": [],
            "growth_rate": 0,
            "trend_direction": "stable",
        }

    def get_business_insights(self) -> dict:
        """Get comprehensive business insights - Advanced business logic"""
        summary = self.reporting_repository.get_global_summary()
        performances = self.reporting_repository.get_store_performances()

        # Calculate business insights
        total_stores = len(performances)
        active_stores = len([p for p in performances if p.sales_count > 0])
        best_store = (
            max(performances, key=lambda x: x.revenue) if performances else None
        )

        insights = {
            "global_summary": self._global_summary_to_response(summary),
            "total_stores": total_stores,
            "active_stores": active_stores,
            "store_activation_rate": (
                (active_stores / total_stores * 100) if total_stores > 0 else 0
            ),
            "best_performing_store": (
                self._store_performance_to_response(best_store) if best_store else None
            ),
            "average_store_revenue": (
                float(sum(p.revenue for p in performances) / len(performances))
                if performances
                else 0
            ),
        }

        return insights

    def _global_summary_to_response(
        self, summary: GlobalSummary
    ) -> GlobalSummaryResponse:
        """Convert domain entity to response schema"""
        return GlobalSummaryResponse(
            total_revenue=summary.total_revenue,
            total_sales_count=summary.total_sales_count,
            average_ticket=summary.average_ticket,
        )

    def _store_performance_to_response(
        self, performance: StorePerformance
    ) -> StorePerformanceResponse:
        """Convert domain entity to response schema"""
        return StorePerformanceResponse(
            store_id=performance.store_id,
            store_name=performance.store_name,
            sales_count=performance.sales_count,
            revenue=performance.revenue,
            average_ticket=performance.average_ticket,
            performance_rating=performance.performance_rating(),
        )

    def _top_product_to_response(self, product: TopProduct) -> TopProductResponse:
        """Convert domain entity to response schema"""
        return TopProductResponse(
            product_code=product.product_code,
            product_name=product.product_name,
            total_quantity_sold=product.total_quantity_sold,
            total_revenue=product.total_revenue,
            total_orders=product.total_orders,
            average_quantity_per_order=product.average_quantity_per_order(),
            average_revenue_per_order=product.average_revenue_per_order(),
        )
