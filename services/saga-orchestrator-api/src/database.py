import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@saga-orchestrator-db:5432/saga_orchestrator_db"
)

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Factory pour les sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Générateur de session de base de données pour les dépendances FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 