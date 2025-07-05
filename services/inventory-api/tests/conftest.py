import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app
from src.database import Base, get_db

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la fonction get_db pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override de la dépendance
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Client de test FastAPI"""
    # Créer les tables de test
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # Nettoyer après les tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Session de base de données pour les tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
