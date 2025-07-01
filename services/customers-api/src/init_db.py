from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .services import CustomerService, AddressService, AuthService
from . import schemas
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialise la base de données avec des données de test"""
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    logger.info("📊 Tables créées")
    
    # Créer une session
    db = SessionLocal()
    
    try:
        # Vérifier si des clients existent déjà
        existing_customers = CustomerService.get_customers(db, limit=1)
        if existing_customers:
            logger.info("✅ Des données existent déjà, pas d'initialisation nécessaire")
            return
        
        logger.info("🔄 Initialisation des données de test...")
        
        # Créer des clients de test
        test_customers = [
            {
                "email": "jean.dupont@email.com",
                "password": "password123",
                "first_name": "Jean",
                "last_name": "Dupont",
                "phone": "+33 1 23 45 67 89"
            },
            {
                "email": "marie.martin@email.com",
                "password": "password123",
                "first_name": "Marie",
                "last_name": "Martin",
                "phone": "+33 1 98 76 54 32"
            },
            {
                "email": "pierre.bernard@email.com",
                "password": "password123",
                "first_name": "Pierre",
                "last_name": "Bernard",
                "phone": "+33 1 11 22 33 44"
            }
        ]
        
        created_customers = []
        for customer_data in test_customers:
            customer_register = schemas.CustomerRegister(**customer_data)
            customer = CustomerService.create_customer(db, customer_register)
            created_customers.append(customer)
            logger.info(f"👤 Client créé: {customer.email} (ID: {customer.id})")
        
        # Créer des adresses de test
        test_addresses = [
            # Adresses pour Jean Dupont
            {
                "customer_id": created_customers[0].id,
                "type": "shipping",
                "title": "Domicile",
                "street_address": "123 Rue de la Paix",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France",
                "is_default": True
            },
            {
                "customer_id": created_customers[0].id,
                "type": "billing",
                "title": "Facturation",
                "street_address": "123 Rue de la Paix",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France",
                "is_default": True
            },
            # Adresses pour Marie Martin
            {
                "customer_id": created_customers[1].id,
                "type": "shipping",
                "title": "Bureau",
                "street_address": "456 Avenue des Champs",
                "city": "Lyon",
                "postal_code": "69001",
                "country": "France",
                "is_default": True
            },
            {
                "customer_id": created_customers[1].id,
                "type": "billing",
                "title": "Domicile",
                "street_address": "789 Boulevard Saint-Germain",
                "city": "Lyon",
                "postal_code": "69002",
                "country": "France",
                "is_default": True
            },
            # Adresse pour Pierre Bernard
            {
                "customer_id": created_customers[2].id,
                "type": "shipping",
                "title": "Maison",
                "street_address": "321 Rue Victor Hugo",
                "city": "Marseille",
                "postal_code": "13001",
                "country": "France",
                "is_default": True
            }
        ]
        
        for address_data in test_addresses:
            customer_id = address_data.pop("customer_id")
            address_create = schemas.AddressCreate(**address_data)
            address = AddressService.create_address(db, customer_id, address_create)
            logger.info(f"📍 Adresse créée: {address.type} pour client {customer_id}")
        
        logger.info("✅ Initialisation terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 