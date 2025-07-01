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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_orders.db"
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
def sample_order_data():
    """Données d'exemple pour créer une commande"""
    return {
        "cart_id": 1,
        "customer_id": 1,
        "shipping_address": {
            "title": "Domicile",
            "street_address": "123 Rue de Test",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        },
        "billing_address": {
            "title": "Domicile",
            "street_address": "123 Rue de Test",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        }
    }

@pytest.fixture
def mock_all_services():
    """Mock de tous les services externes"""
    with respx.mock:
        # Mock Cart API - panier avec articles
        respx.get("http://cart-api:8007/api/v1/carts/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "customer_id": 1,
                    "total_price": 79.97,
                    "total_items": 3,
                    "is_active": True,
                    "items": [
                        {
                            "id": 1,
                            "product_id": 1,
                            "quantity": 2,
                            "unit_price": 29.99,
                            "total_price": 59.98
                        },
                        {
                            "id": 2,
                            "product_id": 2,
                            "quantity": 1,
                            "unit_price": 19.99,
                            "total_price": 19.99
                        }
                    ]
                }
            )
        )
        
        # Mock Products API
        respx.get("http://products-api:8001/api/v1/products/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "nom": "Produit Test 1",
                    "prix": 29.99,
                    "description": "Description du produit test 1",
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
        
        # Mock Stock API
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
                    "quantite_disponible": 50,
                    "stock_minimum": 5,
                    "stock_maximum": 200
                }
            )
        )
        
        # Mock pour réduire le stock
        respx.put("http://stock-api:8004/api/v1/stocks/1/reduce").mock(
            return_value=httpx.Response(
                200,
                json={"message": "Stock réduit avec succès"}
            )
        )
        respx.put("http://stock-api:8004/api/v1/stocks/2/reduce").mock(
            return_value=httpx.Response(
                200,
                json={"message": "Stock réduit avec succès"}
            )
        )
        
        # Mock Cart API - panier vide
        respx.get("http://cart-api:8007/api/v1/carts/999").mock(
            return_value=httpx.Response(404)
        )
        
        yield

@pytest.fixture
def mock_empty_cart():
    """Mock d'un panier vide"""
    with respx.mock:
        respx.get("http://cart-api:8007/api/v1/carts/2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 2,
                    "customer_id": 1,
                    "total_price": 0,
                    "total_items": 0,
                    "is_active": True,
                    "items": []
                }
            )
        )
        yield

@pytest.fixture
def mock_insufficient_stock():
    """Mock avec stock insuffisant"""
    with respx.mock:
        # Mock Cart API avec panier
        respx.get("http://cart-api:8007/api/v1/carts/3").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 3,
                    "customer_id": 1,
                    "total_price": 29.99,
                    "total_items": 10,
                    "is_active": True,
                    "items": [
                        {
                            "id": 1,
                            "product_id": 1,
                            "quantity": 10,
                            "unit_price": 29.99,
                            "total_price": 299.90
                        }
                    ]
                }
            )
        )
        
        # Mock Stock API avec stock insuffisant
        respx.get("http://stock-api:8004/api/v1/stocks/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "product_id": 1,
                    "quantite_disponible": 5,  # Insuffisant pour 10
                    "stock_minimum": 10,
                    "stock_maximum": 500
                }
            )
        )
        
        yield 