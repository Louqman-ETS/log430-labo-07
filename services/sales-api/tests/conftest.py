import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import respx
import httpx
from datetime import datetime

from src.main import app
from src.database import Base, get_db
from src.models import Sale, SaleLine

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sales.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Crée une session de base de données pour les tests"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Crée un client de test FastAPI avec une base de données de test"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_external_services():
    """Mock des services externes pour les tests"""
    with respx.mock() as respx_mock:
        # Mock du service Products
        respx_mock.get("http://products-api:8001/api/v1/products/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "nom": "Test Product",
                    "description": "Un produit de test",
                    "prix": 10.99,
                    "category_id": 1
                }
            )
        )
        
        respx_mock.get("http://products-api:8001/api/v1/products/2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 2,
                    "nom": "Another Product",
                    "description": "Un autre produit",
                    "prix": 5.50,
                    "category_id": 1
                }
            )
        )
        
        # Mock du service Stores
        respx_mock.get("http://stores-api:8002/api/v1/stores/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "nom": "Test Store",
                    "adresse": "123 Test Street",
                    "telephone": "555-0123",
                    "email": "test@store.com"
                }
            )
        )
        
        respx_mock.get("http://stores-api:8002/api/v1/cash-registers/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "numero": 1,
                    "nom": "Caisse 1",
                    "store_id": 1
                }
            )
        )
        
        # Mock du service Stock
        respx_mock.put("http://stock-api:8004/api/v1/products/1/stock/reduce").mock(
            return_value=httpx.Response(
                200,
                json={"success": True, "message": "Stock reduced"}
            )
        )
        
        respx_mock.put("http://stock-api:8004/api/v1/products/2/stock/reduce").mock(
            return_value=httpx.Response(
                200,
                json={"success": True, "message": "Stock reduced"}
            )
        )
        
        # Mock pour les erreurs
        respx_mock.get("http://products-api:8001/api/v1/products/999").mock(
            return_value=httpx.Response(404, json={"detail": "Product not found"})
        )
        
        respx_mock.get("http://stores-api:8002/api/v1/stores/999").mock(
            return_value=httpx.Response(404, json={"detail": "Store not found"})
        )
        
        yield respx_mock

@pytest.fixture
def sample_sale(db_session):
    """Crée une vente de test"""
    sale = Sale(
        store_id=1,
        cash_register_id=1,
        notes="Vente de test",
        total=16.49
    )
    db_session.add(sale)
    db_session.commit()
    db_session.refresh(sale)
    
    # Ajouter des lignes de vente
    sale_line1 = SaleLine(
        sale_id=sale.id,
        product_id=1,
        quantite=1,
        prix_unitaire=10.99,
        sous_total=10.99
    )
    
    sale_line2 = SaleLine(
        sale_id=sale.id,
        product_id=2,
        quantite=1,
        prix_unitaire=5.50,
        sous_total=5.50
    )
    
    db_session.add_all([sale_line1, sale_line2])
    db_session.commit()
    
    return sale

@pytest.fixture
def valid_sale_data():
    """Données valides pour créer une vente"""
    return {
        "store_id": 1,
        "cash_register_id": 1,
        "sale_lines": [
            {
                "product_id": 1,
                "quantite": 2,
                "prix_unitaire": 10.99
            },
            {
                "product_id": 2,
                "quantite": 1,
                "prix_unitaire": 5.50
            }
        ],
        "notes": "Vente de test avec inter-service communication"
    } 