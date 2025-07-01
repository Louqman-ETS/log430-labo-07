import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import respx
import httpx

# Configurer l'environnement de test
os.environ["TESTING"] = "1"

from src.main import app
from src.database import get_db, Base

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cart.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def db_session():
    """Crée une session de base de données pour les tests"""
    # Importer les modèles pour s'assurer qu'ils sont définis
    from src import models
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Client de test FastAPI"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_cart_data():
    """Données d'exemple pour créer un panier"""
    return {
        "customer_id": 1,
        "session_id": None
    }

@pytest.fixture
def sample_guest_cart_data():
    """Données d'exemple pour créer un panier invité"""
    return {
        "customer_id": None,
        "session_id": "guest-session-123"
    }

@pytest.fixture
def sample_product_data():
    """Données d'exemple de produit mockées"""
    return {
        "id": 1,
        "nom": "Produit Test",
        "prix": 29.99,
        "description": "Description du produit test",
        "categorie_nom": "Catégorie Test"
    }

@pytest.fixture
def sample_stock_data():
    """Données d'exemple de stock mockées"""
    return {
        "product_id": 1,
        "quantite_disponible": 100,
        "stock_minimum": 10,
        "stock_maximum": 500
    }

@pytest.fixture
def mock_products_api():
    """Mock de l'API Products"""
    with respx.mock:
        respx.get("http://products-api:8001/api/v1/products/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "nom": "Produit Test",
                    "prix": 29.99,
                    "description": "Description du produit test",
                    "categorie_nom": "Catégorie Test"
                }
            )
        )
        respx.get("http://products-api:8001/api/v1/products/2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 2,
                    "nom": "Produit Test 2",
                    "prix": 19.99,
                    "description": "Description du produit test 2",
                    "categorie_nom": "Catégorie Test"
                }
            )
        )
        respx.get("http://products-api:8001/api/v1/products/999").mock(
            return_value=httpx.Response(404)
        )
        yield

@pytest.fixture
def mock_stock_api():
    """Mock de l'API Stock"""
    with respx.mock:
        respx.get("http://stock-api:8004/api/v1/stocks/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "product_id": 1,
                    "quantite_disponible": 100,
                    "stock_minimum": 10,
                    "stock_maximum": 500
                }
            )
        )
        respx.get("http://stock-api:8004/api/v1/stocks/2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "product_id": 2,
                    "quantite_disponible": 5,
                    "stock_minimum": 10,
                    "stock_maximum": 500
                }
            )
        )
        respx.get("http://stock-api:8004/api/v1/stocks/999").mock(
            return_value=httpx.Response(404)
        )
        yield 