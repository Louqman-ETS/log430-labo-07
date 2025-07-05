import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import httpx
from unittest.mock import AsyncMock, patch

# Import the app and database
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app
from src.database import get_db, Base
from external_services import external_client

# Test database - using in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Database session fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def mock_external_services():
    """Mock external services"""
    with patch(
        "external_services.external_client.get_products"
    ) as mock_products, patch(
        "external_services.external_client.get_stores"
    ) as mock_stores, patch(
        "external_services.external_client.get_product"
    ) as mock_product, patch(
        "external_services.external_client.get_store"
    ) as mock_store:

        # Mock products
        mock_products.return_value = [
            {"id": 1, "nom": "Product 1", "code": "CODE1"},
            {"id": 2, "nom": "Product 2", "code": "CODE2"},
        ]

        # Mock stores
        mock_stores.return_value = [
            {"id": 1, "nom": "Store 1"},
            {"id": 2, "nom": "Store 2"},
        ]

        # Mock individual product
        mock_product.return_value = {"id": 1, "nom": "Product 1", "code": "CODE1"}

        # Mock individual store
        mock_store.return_value = {"id": 1, "nom": "Store 1"}

        yield {
            "products": mock_products,
            "stores": mock_stores,
            "product": mock_product,
            "store": mock_store,
        }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for external API calls"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 1,
                    "total": 100.0,
                    "store_id": 1,
                    "sale_lines": [
                        {"product_id": 1, "quantite": 2, "sous_total": 50.0}
                    ],
                },
                {
                    "id": 2,
                    "total": 200.0,
                    "store_id": 2,
                    "sale_lines": [
                        {"product_id": 2, "quantite": 1, "sous_total": 200.0}
                    ],
                },
            ]
        }
        mock_client_instance.get.return_value = mock_response

        yield mock_client_instance


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database before each test"""
    # Clear all tables
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
