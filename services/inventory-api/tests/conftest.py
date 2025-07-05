import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app
from src.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a new database session for a test."""
    from src.models import Base

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with a test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Create client without context manager
    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_category_data():
    """Données de test pour les catégories"""
    return {
        "id": 1,
        "nom": "Électronique",
        "description": "Produits électroniques",
        "actif": True,
    }


@pytest.fixture
def mock_product_data():
    """Données de test pour les produits"""
    return {
        "id": 1,
        "nom": "Smartphone",
        "description": "Smartphone haut de gamme",
        "prix": 599.99,
        "categorie_id": 1,
        "actif": True,
    }


@pytest.fixture
def mock_stock_data():
    """Données de test pour le stock"""
    return {"id": 1, "product_id": 1, "quantite": 50, "seuil_alerte": 10, "actif": True}
