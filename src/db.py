from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from contextlib import contextmanager
import os
from typing import Generator
from dotenv import load_dotenv

# Configuration par défaut
DEFAULT_CONFIG = {
    "POOL_SIZE": 5,
    "MAX_OVERFLOW": 10,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
}

load_dotenv()


class DatabaseConfig:
    """Configuration de la base de données"""

    def __init__(self):
        self.url = os.getenv("DATABASE_URL")
        if not self.url:
            raise ValueError("DATABASE_URL must be set")

        self.pool_size = int(os.getenv("POOL_SIZE", str(DEFAULT_CONFIG["POOL_SIZE"])))
        self.max_overflow = int(
            os.getenv("MAX_OVERFLOW", str(DEFAULT_CONFIG["MAX_OVERFLOW"]))
        )
        self.pool_timeout = DEFAULT_CONFIG["POOL_TIMEOUT"]
        self.pool_recycle = DEFAULT_CONFIG["POOL_RECYCLE"]


class Database:
    """Gestionnaire de base de données"""

    def __init__(self, config: DatabaseConfig):
        self.engine = create_engine(
            config.url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Retourne une session de base de données dans un contexte géré"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


config = DatabaseConfig()
db = Database(config)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fonction helper pour obtenir une session DB"""
    with db.get_session() as session:
        yield session
