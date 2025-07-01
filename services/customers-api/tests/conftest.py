import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurer l'environnement de test
os.environ["TESTING"] = "1"

from src.main import app
from src.database import get_db, Base

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_customers.db"
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
def sample_customer_data():
    """Données d'exemple pour créer un client"""
    return {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+33123456789"
    }

@pytest.fixture
def sample_address_data():
    """Données d'exemple pour créer une adresse"""
    return {
        "type": "shipping",
        "title": "Domicile",
        "street_address": "123 Rue de Test",
        "city": "Paris",
        "postal_code": "75001",
        "country": "France",
        "is_default": True
    } 