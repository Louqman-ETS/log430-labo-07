from sqlalchemy.orm import Session, sessionmaker
from .database import engine
from .models import Product, Category
import logging

logger = logging.getLogger("products-api")

def init_database():
    """Initialize database with sample data if empty"""
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Category).count() > 0:
            logger.info("Products database already initialized")
            return
        
        logger.info("Initializing Products database...")
        
        # Create categories
        categories_data = [
            {"nom": "Épicerie", "description": "Produits alimentaires de base"},
            {"nom": "Boissons", "description": "Boissons chaudes et froides"},
            {"nom": "Snacks", "description": "Collations et grignotines"},
            {"nom": "Hygiène", "description": "Produits d'hygiène personnelle"},
            {"nom": "Électronique", "description": "Petits appareils électroniques"}
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            categories.append(category)
        
        db.commit()
        
        # Refresh to get IDs
        for category in categories:
            db.refresh(category)
        
        # Create products
        products_data = [
            # Épicerie (category_id=1)
            {"nom": "Pain complet", "description": "Pain complet bio", "prix": 2.50, "category_id": 1},
            {"nom": "Lait 1L", "description": "Lait entier frais", "prix": 1.80, "category_id": 1},
            {"nom": "Œufs x12", "description": "Œufs de poules élevées au sol", "prix": 3.20, "category_id": 1},
            
            # Boissons (category_id=2)
            {"nom": "Eau minérale 1.5L", "description": "Eau minérale naturelle", "prix": 0.85, "category_id": 2},
            {"nom": "Café en grains 250g", "description": "Café arabica torréfié", "prix": 4.90, "category_id": 2},
            {"nom": "Jus d'orange 1L", "description": "Jus d'orange pressé", "prix": 2.70, "category_id": 2},
            
            # Snacks (category_id=3) 
            {"nom": "Chips nature 150g", "description": "Chips de pomme de terre nature", "prix": 1.50, "category_id": 3},
            {"nom": "Chocolat noir 100g", "description": "Chocolat noir 70% cacao", "prix": 2.80, "category_id": 3},
            {"nom": "Biscuits sablés", "description": "Biscuits sablés au beurre", "prix": 2.20, "category_id": 3},
            
            # Hygiène (category_id=4)
            {"nom": "Savon de Marseille", "description": "Savon traditionnel olive", "prix": 1.90, "category_id": 4},
            {"nom": "Dentifrice 75ml", "description": "Dentifrice protection complète", "prix": 2.40, "category_id": 4},
            {"nom": "Shampoing 250ml", "description": "Shampoing tous types cheveux", "prix": 3.50, "category_id": 4},
            
            # Électronique (category_id=5)
            {"nom": "Piles AA x4", "description": "Piles alcalines longue durée", "prix": 3.90, "category_id": 5},
            {"nom": "Câble USB-C 1m", "description": "Câble de charge USB-C", "prix": 8.90, "category_id": 5}
        ]
        
        products = []
        for prod_data in products_data:
            product = Product(**prod_data)
            db.add(product)
            products.append(product)
        
        db.commit()
        
        logger.info(f"✅ Products database initialized with {len(categories_data)} categories and {len(products_data)} products")
    
    except Exception as e:
        logger.error(f"❌ Error initializing Products database: {e}")
        db.rollback()
        raise
    
    finally:
        db.close() 