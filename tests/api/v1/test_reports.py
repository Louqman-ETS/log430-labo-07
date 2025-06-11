import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from src.app.api.main import app
from src.app.api.v1 import dependencies
from src.db import get_db

# Mock DB session
mock_db_session = MagicMock(spec=Session)


def override_get_db():
    try:
        yield mock_db_session
    finally:
        mock_db_session.reset_mock()


def override_api_token_auth():
    pass


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[dependencies.api_token_auth] = override_api_token_auth

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    mock_db_session.reset_mock()
    yield


def test_read_global_summary(client: TestClient, db_session: MagicMock):
    with patch("src.app.api.v1.crud.get_global_summary") as mock_get_summary:
        mock_summary = MagicMock()
        mock_summary.total_revenue = 10000.50
        mock_summary.total_sales_count = 150
        mock_summary.average_ticket = 66.67
        mock_get_summary.return_value = mock_summary

        response = client.get("/api/v1/reports/global-summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 10000.50
        assert data["total_sales_count"] == 150
        assert data["average_ticket"] == 66.67
        mock_get_summary.assert_called_once_with(db_session)


def test_read_performance_by_store(client: TestClient, db_session: MagicMock):
    with patch("src.app.api.v1.crud.get_performance_by_store") as mock_get_performance:
        mock_perf = MagicMock()
        mock_perf.store_id = 1
        mock_perf.store_name = "Main Store"
        mock_perf.sales_count = 50
        mock_perf.revenue = 5000.25
        mock_perf.average_ticket = 100.01
        mock_get_performance.return_value = [mock_perf]

        response = client.get("/api/v1/reports/performance-by-store")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["store_id"] == 1
        assert data[0]["store_name"] == "Main Store"
        assert data[0]["revenue"] == 5000.25
        mock_get_performance.assert_called_once_with(db_session)


def test_read_top_selling_products(client: TestClient, db_session: MagicMock):
    with patch("src.app.api.v1.crud.get_top_selling_products") as mock_get_top_products:
        mock_product = MagicMock()
        mock_product.product_code = "P001"
        mock_product.product_name = "Best Product"
        mock_product.total_quantity_sold = 200
        mock_product.total_revenue = 4000.00
        mock_product.total_orders = 100
        mock_get_top_products.return_value = [mock_product]

        response = client.get("/api/v1/reports/top-selling-products")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_name"] == "Best Product"
        assert data[0]["total_quantity_sold"] == 200
        mock_get_top_products.assert_called_once_with(db_session, store_id=None)


def test_read_top_selling_products_by_store(client: TestClient, db_session: MagicMock):
    with patch("src.app.api.v1.crud.get_top_selling_products") as mock_get_top_products:
        mock_get_top_products.return_value = []

        response = client.get("/api/v1/reports/top-selling-products?store_id=1")

        assert response.status_code == 200
        mock_get_top_products.assert_called_once_with(db_session, store_id=1)
