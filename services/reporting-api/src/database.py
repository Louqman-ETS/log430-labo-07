import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "REPORTING_DATABASE_URL", 
    "postgresql://postgres:password@reporting-db:5432/reporting_db"
)

# Créer l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Créer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 