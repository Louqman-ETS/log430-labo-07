import logging
from sqlalchemy.orm import sessionmaker
from src.database import engine, Base
from src.models import Saga, SagaStepExecution, SagaEvent

logger = logging.getLogger(__name__)


def init_database():
    """Initialise la base de données avec les tables nécessaires"""
    try:
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Vérifier la connexion
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Test simple pour vérifier que la DB fonctionne
            result = session.execute("SELECT 1").fetchone()
            logger.info("✅ Database connection verified")
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    # Permettre l'exécution directe du script
    init_database()
    print("Database initialization completed") 