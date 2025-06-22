import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date

from src.api.main import app
from src.api.v1.dependencies import api_token_auth
from src.api.v1.endpoints.reports import get_reporting_service
from src.api.v1.domain.reporting.schemas.report_schemas import (
    GlobalSummaryResponse,
    StorePerformanceResponse,
    TopProductResponse,
    SalesReportResponse,
)


class TestReportsEndpoints:
    """Test suite for reports endpoints with DDD architecture"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""

        def mock_auth():
            return "test-token"

        app.dependency_overrides[api_token_auth] = mock_auth

        with TestClient(app) as client:
            yield client

        # Clean up
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_reporting_service(self):
        """Mock reporting service"""
        service = MagicMock()
        app.dependency_overrides[get_reporting_service] = lambda: service
        yield service
        # Clean up
        if get_reporting_service in app.dependency_overrides:
            del app.dependency_overrides[get_reporting_service]

    def test_get_global_summary_success(self, client, mock_reporting_service):
        """Test successful retrieval of global summary"""
        # Arrange
        mock_summary = GlobalSummaryResponse(
            total_revenue=Decimal("1250.75"),
            total_sales_count=45,
            average_ticket=Decimal("27.79"),
        )
        mock_reporting_service.get_global_summary.return_value = mock_summary

        # Act
        response = client.get("/api/v1/reports/global-summary")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_revenue"]) == 1250.75
        assert data["total_sales_count"] == 45
        assert float(data["average_ticket"]) == 27.79
        mock_reporting_service.get_global_summary.assert_called_once_with(None, None)

    def test_get_global_summary_with_dates(self, client, mock_reporting_service):
        """Test global summary with date filters"""
        # Arrange
        mock_summary = GlobalSummaryResponse(
            total_revenue=Decimal("500.00"),
            total_sales_count=20,
            average_ticket=Decimal("25.00"),
        )
        mock_reporting_service.get_global_summary.return_value = mock_summary

        # Act
        response = client.get(
            "/api/v1/reports/global-summary?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_revenue"]) == 500.00
        # Verify dates were passed correctly
        args = mock_reporting_service.get_global_summary.call_args[0]
        assert args[0] == date(2024, 1, 1)
        assert args[1] == date(2024, 1, 31)

    def test_get_store_performance_success(self, client, mock_reporting_service):
        """Test successful retrieval of store performance"""
        # Arrange
        mock_performance = StorePerformanceResponse(
            store_id=1,
            store_name="Magasin Centre-Ville",
            sales_count=25,
            revenue=Decimal("750.50"),
            average_ticket=Decimal("30.02"),
            performance_rating="Excellent",
        )
        mock_reporting_service.get_store_performance.return_value = mock_performance

        # Act
        response = client.get("/api/v1/reports/stores/1/performance")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["store_id"] == 1
        assert data["store_name"] == "Magasin Centre-Ville"
        assert data["sales_count"] == 25
        assert float(data["revenue"]) == 750.50
        assert data["performance_rating"] == "Excellent"
        mock_reporting_service.get_store_performance.assert_called_once_with(
            1, None, None
        )

    def test_get_store_performance_not_found(self, client, mock_reporting_service):
        """Test store performance not found"""
        # Arrange
        mock_reporting_service.get_store_performance.return_value = None

        # Act
        response = client.get("/api/v1/reports/stores/999/performance")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_get_all_stores_performance_success(self, client, mock_reporting_service):
        """Test successful retrieval of all stores performance"""
        # Arrange
        mock_performances = [
            StorePerformanceResponse(
                store_id=1,
                store_name="Magasin 1",
                sales_count=30,
                revenue=Decimal("900.00"),
                average_ticket=Decimal("30.00"),
                performance_rating="Excellent",
            ),
            StorePerformanceResponse(
                store_id=2,
                store_name="Magasin 2",
                sales_count=20,
                revenue=Decimal("500.00"),
                average_ticket=Decimal("25.00"),
                performance_rating="Bon",
            ),
        ]
        mock_reporting_service.get_all_stores_performance.return_value = (
            mock_performances
        )

        # Act
        response = client.get("/api/v1/reports/stores/performance")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["store_name"] == "Magasin 1"
        assert data[1]["store_name"] == "Magasin 2"
        mock_reporting_service.get_all_stores_performance.assert_called_once_with(
            None, None, 10
        )

    def test_get_all_stores_performance_with_limit(
        self, client, mock_reporting_service
    ):
        """Test stores performance with custom limit"""
        # Arrange
        mock_reporting_service.get_all_stores_performance.return_value = []

        # Act
        response = client.get("/api/v1/reports/stores/performance?limit=5")

        # Assert
        assert response.status_code == 200
        mock_reporting_service.get_all_stores_performance.assert_called_once_with(
            None, None, 5
        )

    def test_get_top_products_success(self, client, mock_reporting_service):
        """Test successful retrieval of top products"""
        # Arrange
        mock_products = [
            TopProductResponse(
                product_code="PROD001",
                product_name="Produit Top 1",
                total_quantity_sold=150,
                total_revenue=Decimal("1500.00"),
                total_orders=30,
                average_quantity_per_order=Decimal("5.00"),
                average_revenue_per_order=Decimal("50.00"),
            ),
            TopProductResponse(
                product_code="PROD002",
                product_name="Produit Top 2",
                total_quantity_sold=100,
                total_revenue=Decimal("1000.00"),
                total_orders=25,
                average_quantity_per_order=Decimal("4.00"),
                average_revenue_per_order=Decimal("40.00"),
            ),
        ]
        mock_reporting_service.get_top_products.return_value = mock_products

        # Act
        response = client.get("/api/v1/reports/top-products")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["product_code"] == "PROD001"
        assert data[0]["total_quantity_sold"] == 150
        assert float(data[0]["total_revenue"]) == 1500.00
        mock_reporting_service.get_top_products.assert_called_once_with(10, None, None)

    def test_get_top_products_with_limit_and_dates(
        self, client, mock_reporting_service
    ):
        """Test top products with custom limit and date filters"""
        # Arrange
        mock_reporting_service.get_top_products.return_value = []

        # Act
        response = client.get(
            "/api/v1/reports/top-products?limit=5&start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert
        assert response.status_code == 200
        args = mock_reporting_service.get_top_products.call_args[0]
        assert args[0] == 5  # limit
        assert args[1] == date(2024, 1, 1)  # start_date
        assert args[2] == date(2024, 1, 31)  # end_date

    def test_get_sales_by_period_success(self, client, mock_reporting_service):
        """Test successful retrieval of sales by period"""
        # Arrange
        mock_sales_report = SalesReportResponse(
            period="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            store_id=None,
            total_sales=50,
            total_revenue=Decimal("2500.00"),
            sales_data=[
                {"date": "2024-01-01", "sales": 5, "revenue": 250.00},
                {"date": "2024-01-02", "sales": 8, "revenue": 400.00},
            ],
        )
        mock_reporting_service.get_sales_by_period.return_value = mock_sales_report

        # Act
        response = client.get("/api/v1/reports/sales-by-period?period=monthly")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "monthly"
        assert data["total_sales"] == 50
        assert float(data["total_revenue"]) == 2500.00
        assert len(data["sales_data"]) == 2
        mock_reporting_service.get_sales_by_period.assert_called_once_with(
            "monthly", None, None, None
        )

    def test_get_sales_by_period_invalid_period(self, client, mock_reporting_service):
        """Test sales by period with invalid period"""
        # Act
        response = client.get("/api/v1/reports/sales-by-period?period=invalid")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_get_sales_by_period_with_store_filter(
        self, client, mock_reporting_service
    ):
        """Test sales by period with store filter"""
        # Arrange
        mock_sales_report = SalesReportResponse(
            period="weekly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            store_id=1,
            total_sales=10,
            total_revenue=Decimal("500.00"),
            sales_data=[],
        )
        mock_reporting_service.get_sales_by_period.return_value = mock_sales_report

        # Act
        response = client.get(
            "/api/v1/reports/sales-by-period?period=weekly&store_id=1"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["store_id"] == 1
        mock_reporting_service.get_sales_by_period.assert_called_once_with(
            "weekly", None, None, 1
        )

    def test_get_inventory_status_success(self, client, mock_reporting_service):
        """Test successful retrieval of inventory status"""
        # Arrange
        mock_inventory = {
            "low_stock_threshold": 10,
            "store_id": None,
            "low_stock_products": [
                {"code": "PROD001", "name": "Produit 1", "stock": 5},
                {"code": "PROD002", "name": "Produit 2", "stock": 8},
            ],
            "out_of_stock_products": [
                {"code": "PROD003", "name": "Produit 3", "stock": 0}
            ],
            "total_products": 50,
            "inventory_value": 25000.00,
        }
        mock_reporting_service.get_inventory_status.return_value = mock_inventory

        # Act
        response = client.get("/api/v1/reports/inventory-status")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["low_stock_threshold"] == 10
        assert len(data["low_stock_products"]) == 2
        assert len(data["out_of_stock_products"]) == 1
        assert data["total_products"] == 50
        mock_reporting_service.get_inventory_status.assert_called_once_with(10, None)

    def test_get_inventory_status_with_filters(self, client, mock_reporting_service):
        """Test inventory status with custom threshold and store filter"""
        # Arrange
        mock_reporting_service.get_inventory_status.return_value = {}

        # Act
        response = client.get(
            "/api/v1/reports/inventory-status?low_stock_threshold=5&store_id=2"
        )

        # Assert
        assert response.status_code == 200
        mock_reporting_service.get_inventory_status.assert_called_once_with(5, 2)

    def test_get_revenue_trends_success(self, client, mock_reporting_service):
        """Test successful retrieval of revenue trends"""
        # Arrange
        mock_trends = {
            "period": "monthly",
            "months_back": 12,
            "store_id": None,
            "trends": [
                {"month": "2024-01", "revenue": 1000.00, "growth": 5.2},
                {"month": "2024-02", "revenue": 1200.00, "growth": 20.0},
            ],
            "growth_rate": 12.6,
            "trend_direction": "croissant",
        }
        mock_reporting_service.get_revenue_trends.return_value = mock_trends

        # Act
        response = client.get("/api/v1/reports/revenue-trends")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "monthly"
        assert data["months_back"] == 12
        assert data["growth_rate"] == 12.6
        assert data["trend_direction"] == "croissant"
        assert len(data["trends"]) == 2
        mock_reporting_service.get_revenue_trends.assert_called_once_with(
            "monthly", 12, None
        )

    def test_get_revenue_trends_with_custom_params(
        self, client, mock_reporting_service
    ):
        """Test revenue trends with custom parameters"""
        # Arrange
        mock_reporting_service.get_revenue_trends.return_value = {}

        # Act
        response = client.get(
            "/api/v1/reports/revenue-trends?period=weekly&months_back=6&store_id=3"
        )

        # Assert
        assert response.status_code == 200
        mock_reporting_service.get_revenue_trends.assert_called_once_with(
            "weekly", 6, 3
        )

    def test_get_revenue_trends_invalid_period(self, client, mock_reporting_service):
        """Test revenue trends with invalid period"""
        # Act
        response = client.get("/api/v1/reports/revenue-trends?period=invalid")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_business_logic_error_handling(self, client, mock_reporting_service):
        """Test business logic error handling"""
        # Arrange
        mock_reporting_service.get_global_summary.side_effect = Exception(
            "Database error"
        )

        # Act
        response = client.get("/api/v1/reports/global-summary")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "BUSINESS_LOGIC_ERROR"
        assert "Failed to generate global summary" in data["message"]

    def test_unauthorized_access(self, mock_reporting_service):
        """Test unauthorized access without token"""
        # Arrange
        client = TestClient(app)  # Client without mocked auth

        # Act
        response = client.get("/api/v1/reports/global-summary")

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "HTTP_ERROR"
