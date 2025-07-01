import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration pour les tests
def get_database_url():
    """Retourne l'URL de la base de données selon l'environnement"""
    if os.getenv("TESTING"):
        return "sqlite:///./test.db"
    else:
        return "postgresql://user:password@products-db:5432/products_db"

def get_engine():
    """Crée le moteur de base de données"""
    database_url = get_database_url()
    
    if "sqlite" in database_url:
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        return create_engine(database_url)

def get_session_local():
    """Crée la classe de session locale"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine) 