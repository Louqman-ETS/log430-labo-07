from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

os.makedirs("data", exist_ok=True)

# Utiliser un chemin relatif pour la base de données
DATABASE_URL = "sqlite:///data/store.db"

# Créer le moteur avec les paramètres appropriés
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Configuration des paramètres SQLite pour une meilleure gestion des erreurs
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 