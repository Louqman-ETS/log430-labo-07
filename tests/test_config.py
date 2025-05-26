import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.db import Base, DatabaseConfig


class TestDatabaseConfig(DatabaseConfig):
    """Configuration de la base de données pour les tests"""

    def __init__(self):
        self.url = os.getenv(
            "DATABASE_URL", "postgresql://user:password@localhost:5432/store_db"
        )
        self.pool_size = 5
        self.max_overflow = 10
        self.pool_timeout = 30
        self.pool_recycle = 1800


class TestDatabase:
    """Gestionnaire de base de données pour les tests"""

    def __init__(self):
        config = TestDatabaseConfig()
        self.engine = create_engine(config.url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def setup(self):
        """Configure la base de données de test"""
        Base.metadata.create_all(self.engine)

    def cleanup(self):
        """Nettoie la base de données de test"""
        Base.metadata.drop_all(self.engine)


# Instance globale pour les tests
test_db = TestDatabase()


def setup_test_database():
    """Configure la base de données de test et retourne l'engine"""
    config = TestDatabaseConfig()
    engine = create_engine(config.url)
    Base.metadata.create_all(engine)
    return engine


def cleanup_test_database(engine):
    """Nettoie la base de données de test"""
    Base.metadata.drop_all(engine)


def get_test_session(engine):
    """Retourne une session de test"""
    Session = sessionmaker(bind=engine)
    return Session()
