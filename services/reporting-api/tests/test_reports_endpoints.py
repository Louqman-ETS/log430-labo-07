import pytest
from unittest.mock import patch, AsyncMock
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
    
    @pytest.mark.asyncio
    async def test_global_summary_success(self, client, mock_httpx_client, mock_external_services):
        """Test global summary endpoint with successful external API calls"""
        with patch("services.ReportingService.get_global_summary") as mock_get_summary:
            mock_get_summary.return_value = {
                "total_sales": 3,
                "total_revenue": 461.24,
                "total_products": 5,
                "total_stores": 5,
                "average_sale_amount": 153.75
            }
            
            response = client.get("/api/v1/reports/global-summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total_sales"] == 3
            assert data["total_revenue"] == 461.24
            assert data["total_products"] == 5
            assert data["total_stores"] == 5
            assert data["average_sale_amount"] == 153.75
    
    @pytest.mark.asyncio
    async def test_global_summary_external_api_error(self, client):
        """Test global summary endpoint when external API fails"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Mock failed response
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_client_instance.get.return_value = mock_response
            
            response = client.get("/api/v1/reports/global-summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total_sales"] == 0
            assert data["total_revenue"] == 0.0
            assert data["average_sale_amount"] == 0.0
    
    @pytest.mark.asyncio
    async def test_store_performances_success(self, client, mock_httpx_client):
        """Test store performances endpoint"""
        with patch("services.ReportingService.get_store_performances") as mock_get_performances:
            mock_get_performances.return_value = [
                {
                    "store_id": 1,
                    "store_name": "Magasin Centre-Ville",
                    "sales_count": 2,
                    "revenue": 215.49,
                    "average_sale_amount": 107.745,
                    "performance_rating": "Below Average"
                },
                {
                    "store_id": 2,
                    "store_name": "Magasin Westmount",
                    "sales_count": 1,
                    "revenue": 245.75,
                    "average_sale_amount": 245.75,
                    "performance_rating": "Below Average"
                }
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
    
    @pytest.mark.asyncio
    async def test_top_stores_endpoint(self, client):
        """Test top stores endpoint with limit parameter"""
        with patch("services.ReportingService.get_store_performances") as mock_get_performances:
            mock_get_performances.return_value = [
                {"store_id": 1, "store_name": "Store 1", "sales_count": 10, "revenue": 1000.0, "average_sale_amount": 100.0, "performance_rating": "Good"},
                {"store_id": 2, "store_name": "Store 2", "sales_count": 8, "revenue": 800.0, "average_sale_amount": 100.0, "performance_rating": "Good"},
                {"store_id": 3, "store_name": "Store 3", "sales_count": 5, "revenue": 500.0, "average_sale_amount": 100.0, "performance_rating": "Average"}
            ]
            
            response = client.get("/api/v1/reports/top-stores?limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 2
    
    @pytest.mark.asyncio
    async def test_underperforming_stores_endpoint(self, client):
        """Test underperforming stores endpoint"""
        with patch("services.ReportingService.get_store_performances") as mock_get_performances:
            mock_get_performances.return_value = [
                {"store_id": 1, "store_name": "Store 1", "sales_count": 10, "revenue": 500.0, "average_sale_amount": 50.0, "performance_rating": "Below Average"},
                {"store_id": 2, "store_name": "Store 2", "sales_count": 8, "revenue": 1200.0, "average_sale_amount": 150.0, "performance_rating": "Good"},
                {"store_id": 3, "store_name": "Store 3", "sales_count": 5, "revenue": 800.0, "average_sale_amount": 160.0, "performance_rating": "Good"}
            ]
            
            response = client.get("/api/v1/reports/underperforming-stores?threshold=1000.0")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 3
    
    @pytest.mark.asyncio
    async def test_top_products_success(self, client, mock_httpx_client):
        """Test top products endpoint"""
        with patch("services.ReportingService.get_top_products") as mock_get_products:
            mock_get_products.return_value = [
                {
                    "product_id": 4,
                    "product_name": "Smartphone Galaxy",
                    "product_code": "ELE001",
                    "total_quantity_sold": 1,
                    "total_revenue": 199.99,
                    "sales_count": 1
                },
                {
                    "product_id": 1,
                    "product_name": "Pain complet",
                    "product_code": "ALI001",
                    "total_quantity_sold": 2,
                    "total_revenue": 50.0,
                    "sales_count": 1
                }
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
    
    @pytest.mark.asyncio
    async def test_products_by_revenue_endpoint(self, client):
        """Test products by revenue endpoint"""
        with patch("services.ReportingService.get_top_products") as mock_get_products:
            mock_get_products.return_value = [
                {"product_id": 1, "product_name": "Product 1", "product_code": "CODE1", "total_quantity_sold": 10, "total_revenue": 1000.0, "sales_count": 5},
                {"product_id": 2, "product_name": "Product 2", "product_code": "CODE2", "total_quantity_sold": 8, "total_revenue": 800.0, "sales_count": 4}
            ]
            
            response = client.get("/api/v1/reports/products-by-revenue?limit=3")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["total_revenue"] == 1000.0
            assert data[1]["total_revenue"] == 800.0
    
    @pytest.mark.asyncio
    async def test_products_by_volume_endpoint(self, client):
        """Test products by volume endpoint"""
        with patch("services.ReportingService.get_top_products") as mock_get_products:
            mock_get_products.return_value = [
                {"product_id": 1, "product_name": "Product 1", "product_code": "CODE1", "total_quantity_sold": 15, "total_revenue": 750.0, "sales_count": 5},
                {"product_id": 2, "product_name": "Product 2", "product_code": "CODE2", "total_quantity_sold": 10, "total_revenue": 1000.0, "sales_count": 4},
                {"product_id": 3, "product_name": "Product 3", "product_code": "CODE3", "total_quantity_sold": 8, "total_revenue": 800.0, "sales_count": 3}
            ]
            
            response = client.get("/api/v1/reports/products-by-volume?limit=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["total_quantity_sold"] == 15
            assert data[1]["total_quantity_sold"] == 10
    
    @pytest.mark.asyncio
    async def test_store_performance_specific_store(self, client):
        """Test store performance for specific store"""
        with patch("services.ReportingService.get_store_performance") as mock_get_performance:
            mock_get_performance.return_value = {
                "store_id": 1,
                "store_name": "Magasin Centre-Ville",
                "sales_count": 5,
                "revenue": 500.0,
                "average_sale_amount": 100.0,
                "performance_rating": "Below Average"
            }
            
            response = client.get("/api/v1/reports/store/1/performance")
            assert response.status_code == 200
            data = response.json()
            assert data["store_id"] == 1
            assert data["store_name"] == "Magasin Centre-Ville"
            assert data["sales_count"] == 5
            assert data["revenue"] == 500.0
    
    @pytest.mark.asyncio
    async def test_store_performance_not_found(self, client):
        """Test store performance for non-existent store"""
        with patch("services.ReportingService.get_store_performance") as mock_get_performance:
            mock_get_performance.return_value = None
            
            response = client.get("/api/v1/reports/store/999/performance")
            assert response.status_code == 404
            data = response.json()
            # Accepte les deux formats d'erreur
            if "error" in data:
                assert "not found" in data["error"]["message"].lower()
            elif "detail" in data:
                assert "not found" in data["detail"].lower()
            else:
                assert False, f"Erreur inattendue: {data}"
    
    @pytest.mark.asyncio
    async def test_all_stores_performance_endpoint(self, client):
        """Test all stores performance endpoint"""
        with patch("services.ReportingService.get_store_performances") as mock_get_performances:
            mock_get_performances.return_value = [
                {"store_id": 1, "store_name": "Store 1", "sales_count": 10, "revenue": 1000.0, "average_sale_amount": 100.0, "performance_rating": "Good"},
                {"store_id": 2, "store_name": "Store 2", "sales_count": 8, "revenue": 800.0, "average_sale_amount": 100.0, "performance_rating": "Good"}
            ]
            
            response = client.get("/api/v1/reports/all-stores-performance")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["store_id"] == 1
            assert data[1]["store_id"] == 2
    
    @pytest.mark.asyncio
    async def test_business_insights_endpoint(self, client):
        """Test business insights endpoint"""
        with patch("services.ReportingService.get_global_summary") as mock_summary, \
             patch("services.ReportingService.get_store_performances") as mock_performances, \
             patch("services.ReportingService.get_top_products") as mock_products:
            
            mock_summary.return_value = {
                "total_sales": 10,
                "total_revenue": 1000.0,
                "total_products": 5,
                "total_stores": 3,
                "average_sale_amount": 100.0
            }
            
            mock_performances.return_value = [
                {"store_id": 1, "store_name": "Store 1", "sales_count": 5, "revenue": 500.0, "average_sale_amount": 100.0, "performance_rating": "Good"}
            ]
            
            mock_products.return_value = [
                {"product_id": 1, "product_name": "Top Product", "product_code": "CODE1", "total_quantity_sold": 10, "total_revenue": 500.0, "sales_count": 5}
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
        assert "message" in data
    
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
        assert data["period_days"] == 30
        assert "message" in data
    
    def test_invalid_period_parameter(self, client):
        """Test invalid period parameter"""
        response = client.get("/api/v1/reports/sales-by-period?period=invalid")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_limit_parameter(self, client):
        """Test invalid limit parameter"""
        response = client.get("/api/v1/reports/top-products?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_negative_threshold_parameter(self, client):
        """Test negative threshold parameter"""
        response = client.get("/api/v1/reports/underperforming-stores?threshold=-100")
        assert response.status_code == 422  # Validation error 