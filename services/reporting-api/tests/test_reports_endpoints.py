import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


class TestReportsEndpoints:
    """Test suite for reporting endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "reporting"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Reporting API is running"
        assert data["service"] == "reporting"
        assert "version" in data
        assert "docs" in data
        assert "features" in data

    def test_global_summary_success(self, client):
        """Test global summary endpoint with successful external API calls"""
        with patch(
            "src.services.ReportingService.get_global_summary"
        ) as mock_get_summary:
            mock_get_summary.return_value = {
                "total_sales": 3,
                "total_revenue": 461.24,
                "total_products": 5,
                "total_stores": 5,
                "average_sale_amount": 153.75,
            }

            response = client.get("/api/v1/reports/global-summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total_sales"] == 3
            assert data["total_revenue"] == 461.24
            assert data["total_products"] == 5
            assert data["total_stores"] == 5
            assert data["average_sale_amount"] == 153.75

    def test_global_summary_external_api_error(self, client):
        """Test global summary endpoint when external API fails"""
        with patch(
            "src.services.ReportingService.get_global_summary"
        ) as mock_get_summary:
            mock_get_summary.return_value = {
                "total_sales": 0,
                "total_revenue": 0.0,
                "total_products": 0,
                "total_stores": 0,
                "average_sale_amount": 0.0,
            }

            response = client.get("/api/v1/reports/global-summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total_sales"] == 0
            assert data["total_revenue"] == 0.0
            assert data["average_sale_amount"] == 0.0

    def test_store_performances_success(self, client):
        """Test store performances endpoint"""
        with patch(
            "src.services.ReportingService.get_store_performances"
        ) as mock_get_performances:
            mock_get_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Magasin Centre-Ville",
                    "sales_count": 2,
                    "revenue": 215.49,
                    "average_sale_amount": 107.745,
                    "performance_rating": "Below Average",
                },
                {
                    "store_id": 2,
                    "store_name": "Magasin Westmount",
                    "sales_count": 1,
                    "revenue": 245.75,
                    "average_sale_amount": 245.75,
                    "performance_rating": "Below Average",
                },
            ]

            response = client.get("/api/v1/reports/store-performances")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[0]["store_name"] == "Magasin Centre-Ville"
            assert data[0]["sales_count"] == 2
            assert data[0]["revenue"] == 215.49
            assert data[1]["store_id"] == 2
            assert data[1]["store_name"] == "Magasin Westmount"

    def test_top_stores_endpoint(self, client):
        """Test top stores endpoint with limit parameter"""
        with patch(
            "src.services.ReportingService.get_store_performances"
        ) as mock_get_performances:
            mock_get_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Store 1",
                    "sales_count": 10,
                    "revenue": 1000.0,
                    "average_sale_amount": 100.0,
                    "performance_rating": "Good",
                },
                {
                    "store_id": 2,
                    "store_name": "Store 2",
                    "sales_count": 8,
                    "revenue": 800.0,
                    "average_sale_amount": 100.0,
                    "performance_rating": "Good",
                },
                {
                    "store_id": 3,
                    "store_name": "Store 3",
                    "sales_count": 5,
                    "revenue": 500.0,
                    "average_sale_amount": 100.0,
                    "performance_rating": "Average",
                },
            ]

            response = client.get("/api/v1/reports/top-stores?limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 2

    def test_underperforming_stores_endpoint(self, client):
        """Test underperforming stores endpoint"""
        with patch(
            "src.services.ReportingService.get_store_performances"
        ) as mock_get_performances:
            mock_get_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Store 1",
                    "sales_count": 10,
                    "revenue": 500.0,
                    "average_sale_amount": 50.0,
                    "performance_rating": "Below Average",
                },
                {
                    "store_id": 2,
                    "store_name": "Store 2",
                    "sales_count": 8,
                    "revenue": 1200.0,
                    "average_sale_amount": 150.0,
                    "performance_rating": "Good",
                },
                {
                    "store_id": 3,
                    "store_name": "Store 3",
                    "sales_count": 5,
                    "revenue": 800.0,
                    "average_sale_amount": 160.0,
                    "performance_rating": "Good",
                },
            ]

            response = client.get(
                "/api/v1/reports/underperforming-stores?threshold=1000.0"
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 3

    def test_top_products_success(self, client):
        """Test top products endpoint"""
        with patch(
            "src.services.ReportingService.get_top_products"
        ) as mock_get_products:
            mock_get_products.return_value = [
                {
                    "product_id": 4,
                    "product_name": "Smartphone Galaxy",
                    "product_code": "ELE001",
                    "total_quantity_sold": 1,
                    "total_revenue": 199.99,
                    "sales_count": 1,
                },
                {
                    "product_id": 1,
                    "product_name": "Pain complet",
                    "product_code": "ALI001",
                    "total_quantity_sold": 2,
                    "total_revenue": 50.0,
                    "sales_count": 1,
                },
            ]

            response = client.get("/api/v1/reports/top-products?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["product_id"] == 4
            assert data[0]["product_name"] == "Smartphone Galaxy"
            assert data[0]["total_revenue"] == 199.99
            assert data[1]["product_id"] == 1
            assert data[1]["product_name"] == "Pain complet"

    def test_products_by_revenue_endpoint(self, client):
        """Test products by revenue endpoint"""
        with patch(
            "src.services.ReportingService.get_top_products"
        ) as mock_get_products:
            mock_get_products.return_value = [
                {
                    "product_id": 1,
                    "product_name": "High Revenue Product",
                    "product_code": "HRP001",
                    "total_quantity_sold": 10,
                    "total_revenue": 1000.0,
                    "sales_count": 5,
                },
                {
                    "product_id": 2,
                    "product_name": "Medium Revenue Product",
                    "product_code": "MRP002",
                    "total_quantity_sold": 15,
                    "total_revenue": 750.0,
                    "sales_count": 3,
                },
            ]

            response = client.get("/api/v1/reports/products-by-revenue?limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["product_name"] == "High Revenue Product"
            assert data[1]["product_name"] == "Medium Revenue Product"

    def test_products_by_volume_endpoint(self, client):
        """Test products by volume endpoint"""
        with patch(
            "src.services.ReportingService.get_top_products"
        ) as mock_get_products:
            mock_get_products.return_value = [
                {
                    "product_id": 1,
                    "product_name": "High Volume Product",
                    "product_code": "HVP001",
                    "total_quantity_sold": 100,
                    "total_revenue": 500.0,
                    "sales_count": 10,
                },
                {
                    "product_id": 2,
                    "product_name": "Medium Volume Product",
                    "product_code": "MVP002",
                    "total_quantity_sold": 75,
                    "total_revenue": 750.0,
                    "sales_count": 5,
                },
            ]

            response = client.get("/api/v1/reports/products-by-volume?limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

    def test_store_performance_specific_store(self, client):
        """Test performance endpoint for specific store"""
        with patch(
            "src.services.ReportingService.get_store_performance"
        ) as mock_get_performance:
            mock_get_performance.return_value = {
                "store_id": 1,
                "store_name": "Test Store",
                "sales_count": 5,
                "revenue": 1000.0,
                "average_sale_amount": 200.0,
                "performance_rating": "Good",
            }

            response = client.get("/api/v1/reports/store/1/performance")
            assert response.status_code == 200
            data = response.json()
            assert data["store_id"] == 1
            assert data["store_name"] == "Test Store"

    def test_store_performance_not_found(self, client):
        """Test performance endpoint for non-existent store"""
        with patch(
            "src.services.ReportingService.get_store_performance"
        ) as mock_get_performance:
            mock_get_performance.return_value = None

            response = client.get("/api/v1/reports/store/999/performance")
            assert response.status_code == 404

    def test_all_stores_performance_endpoint(self, client):
        """Test all stores performance endpoint"""
        with patch(
            "src.services.ReportingService.get_store_performances"
        ) as mock_get_performances:
            mock_get_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Store 1",
                    "sales_count": 10,
                    "revenue": 1000.0,
                    "average_sale_amount": 100.0,
                    "performance_rating": "Good",
                },
                {
                    "store_id": 2,
                    "store_name": "Store 2",
                    "sales_count": 8,
                    "revenue": 800.0,
                    "average_sale_amount": 100.0,
                    "performance_rating": "Good",
                },
            ]

            response = client.get("/api/v1/reports/all-stores-performance")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 2

    def test_business_insights_endpoint(self, client):
        """Test business insights endpoint"""
        with patch(
            "src.services.ReportingService.get_global_summary"
        ) as mock_summary, patch(
            "src.services.ReportingService.get_store_performances"
        ) as mock_performances, patch(
            "src.services.ReportingService.get_top_products"
        ) as mock_products:

            mock_summary.return_value = {
                "total_sales": 10,
                "total_revenue": 5000.0,
                "total_products": 20,
                "total_stores": 5,
                "average_sale_amount": 500.0,
            }

            mock_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Top Store",
                    "sales_count": 10,
                    "revenue": 2000.0,
                    "average_sale_amount": 200.0,
                    "performance_rating": "Excellent",
                }
            ]

            mock_products.return_value = [
                {
                    "product_id": 1,
                    "product_name": "Top Product",
                    "product_code": "TOP001",
                    "total_quantity_sold": 50,
                    "total_revenue": 1000.0,
                    "sales_count": 10,
                }
            ]

            response = client.get("/api/v1/reports/business-insights")
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "insights" in data
            assert "top_performing_stores" in data
            assert "top_products" in data

    def test_sales_by_period_mock_endpoint(self, client):
        """Test sales by period mock endpoint"""
        response = client.get("/api/v1/reports/sales-by-period?period=month")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "month"

    def test_inventory_status_mock_endpoint(self, client):
        """Test inventory status mock endpoint"""
        response = client.get("/api/v1/reports/inventory-status")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "low_stock_items" in data
        assert "out_of_stock_items" in data

    def test_revenue_trends_mock_endpoint(self, client):
        """Test revenue trends mock endpoint"""
        response = client.get("/api/v1/reports/revenue-trends?days=30")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_invalid_period_parameter(self, client):
        """Test invalid period parameter"""
        response = client.get("/api/v1/reports/sales-by-period?period=invalid")
        assert response.status_code == 422

    def test_invalid_limit_parameter(self, client):
        """Test invalid limit parameter"""
        response = client.get("/api/v1/reports/top-stores?limit=0")
        assert response.status_code == 422

    def test_negative_threshold_parameter(self, client):
        """Test negative threshold parameter"""
        response = client.get("/api/v1/reports/underperforming-stores?threshold=-100")
        assert response.status_code == 422
