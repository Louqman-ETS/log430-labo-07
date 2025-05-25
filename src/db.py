from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration PostgreSQL depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))

# Créer le moteur pour PostgreSQL avec une configuration plus robuste
engine = create_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=30,  # timeout de 30 secondes pour obtenir une connexion
    pool_recycle=1800  # recycler les connexions après 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Retourne une nouvelle session de base de données"""
    return SessionLocal()
