import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base

# Configuration pour les tests
def get_test_database_url():
    """Retourne l'URL de la base de données de test"""
    return os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/store_db"
    )

def create_test_engine():
    """Crée un moteur de base de données pour les tests"""
    database_url = get_test_database_url()
    return create_engine(database_url)

def setup_test_database():
    """Configure la base de données de test"""
    engine = create_test_engine()
    
    # Créer toutes les tables
    Base.metadata.create_all(engine)
    
    return engine

def cleanup_test_database(engine):
    """Nettoie la base de données de test"""
    # Supprimer toutes les tables
    Base.metadata.drop_all(engine)

def get_test_session(engine):
    """Retourne une session de test"""
    TestSession = sessionmaker(bind=engine)
    return TestSession() 