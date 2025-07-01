from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration conditionnelle pour les tests
def get_database_url():
    """Retourne l'URL de la base de données selon l'environnement"""
    if os.getenv("TESTING"):
        return "sqlite:///./test_orders.db"
    else:
        return os.getenv("ORDERS_DATABASE_URL", "postgresql://postgres:password@orders-db:5432/orders_db")

def create_database_engine():
    """Crée le moteur de base de données"""
    database_url = get_database_url()
    
    if "sqlite" in database_url:
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        return create_engine(database_url)

# Créer les objets de base de données
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 