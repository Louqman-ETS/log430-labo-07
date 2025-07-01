from sqlalchemy.orm import Session, sessionmaker
from .database import engine
from .models import Store, CashRegister
import logging

logger = logging.getLogger("stores-api")

def init_database():
    """Initialize database with sample data if empty"""
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Store).count() > 0:
            logger.info("Stores database already initialized")
            return
        
        logger.info("Initializing Stores database...")
        
        # Create stores
        stores_data = [
            {
                "nom": "Magasin Centre-Ville",
                "adresse": "123 Rue Principale",
                "telephone": "514-555-0001",
                "email": "centre@magasin.com",
            },
            {
                "nom": "Magasin Banlieue",
                "adresse": "456 Avenue des Érables",
                "telephone": "514-555-0002",
                "email": "banlieue@magasin.com",
            },
            {
                "nom": "Magasin Nord",
                "adresse": "789 Boulevard Nord",
                "telephone": "514-555-0003",
                "email": "nord@magasin.com",
            },
            {
                "nom": "Magasin Sud",
                "adresse": "321 Rue du Sud",
                "telephone": "514-555-0004",
                "email": "sud@magasin.com",
            },
            {
                "nom": "Magasin Express",
                "adresse": "654 Avenue Express",
                "telephone": "514-555-0005",
                "email": "express@magasin.com",
            },
        ]
        
        stores = []
        for store_data in stores_data:
            store = Store(**store_data)
            db.add(store)
            stores.append(store)
        
        db.commit()
        
        # Refresh to get IDs
        for store in stores:
            db.refresh(store)
        
        # Create cash registers for each store (3 per store)
        cash_registers = []
        for store in stores:
            for i in range(1, 4):  # Cash registers 1, 2, 3
                cash_register = CashRegister(
                    numero=i,
                    nom=f"Caisse {i}",
                    store_id=store.id
                )
                db.add(cash_register)
                cash_registers.append(cash_register)
        
        db.commit()
        
        logger.info(f"✅ Stores database initialized with {len(stores_data)} stores and {len(cash_registers)} cash registers") 
    
    except Exception as e:
        logger.error(f"❌ Error initializing Stores database: {e}")
        db.rollback()
        raise
    
    finally:
        db.close() 