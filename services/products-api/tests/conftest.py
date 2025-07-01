import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import tempfile
import os

# Définir la variable d'environnement pour les tests
os.environ["TESTING"] = "1"

from src.main import app
from src.database import Base, get_db
from src.models import Category, Product

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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
def sample_category(db_session):
    """Crée une catégorie de test"""
    category = Category(
        nom="Test Category",
        description="Une catégorie de test"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def sample_product(db_session, sample_category):
    """Crée un produit de test"""
    product = Product(
        code="TEST001",
        nom="Test Product",
        description="Un produit de test",
        prix=9.99,
        categorie_id=sample_category.id
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def multiple_products(db_session, sample_category):
    """Crée plusieurs produits pour les tests de pagination"""
    products = []
    for i in range(15):
        product = Product(
            code=f"PROD{i+1:03d}",
            nom=f"Product {i+1}",
            description=f"Description du produit {i+1}",
            prix=float(i + 1),
            categorie_id=sample_category.id
        )
        db_session.add(product)
        products.append(product)
    
    db_session.commit()
    for product in products:
        db_session.refresh(product)
    return products 