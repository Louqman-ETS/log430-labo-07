import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration pour les tests
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test_saga.db"

from src.main import app
from src.database import get_db, Base


# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_saga.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la session de base de données pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override de la dépendance
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Client de test FastAPI"""
    # Créer les tables pour les tests
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Nettoyer après les tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_order_request():
    """Exemple de requête de commande pour les tests"""
    return {
        "customer_id": 1,
        "cart_id": 123,
        "products": [
            {"product_id": 1, "quantity": 2, "price": 29.99},
            {"product_id": 2, "quantity": 1, "price": 59.99}
        ],
        "shipping_address": "123 Test St, City, State, ZIP",
        "billing_address": "123 Test St, City, State, ZIP",
        "payment_method": "credit_card"
    } 