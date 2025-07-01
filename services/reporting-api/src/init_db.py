from sqlalchemy.orm import Session, sessionmaker
from .database import engine
from datetime import datetime, timedelta
import random
import logging
from .models import Sale, SaleLine, StoreStock, CentralStock, RestockingRequest

logger = logging.getLogger("reporting-api")

def init_database():
    """Initialize database with sample data if empty"""
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Sale).count() > 0:
            logger.info("Reporting database already initialized")
            return
        
        logger.info("Initializing Reporting database...")
        
        # Sample data for sales (simulating sales across stores and products)
        sample_sales = []
        
        # Create some sample sales over the past 30 days
        for i in range(50):  # 50 sample sales
            # Random store ID (1-5) and cash register ID (1-15, 3 per store)
            store_id = random.randint(1, 5)
            cash_register_id = (store_id - 1) * 3 + random.randint(1, 3)
            
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            sale_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Random total amount
            montant_total = round(random.uniform(10.0, 150.0), 2)
            
            sale = Sale(
                date_heure=sale_date,
                montant_total=montant_total,
                store_id=store_id,
                cash_register_id=cash_register_id
            )
            db.add(sale)
            sample_sales.append(sale)
        
        db.commit()
        
        # Refresh to get IDs
        for sale in sample_sales:
            db.refresh(sale)
        
        # Create sale lines for each sale
        sale_lines = []
        for sale in sample_sales:
            # Each sale has 1-4 products
            num_products = random.randint(1, 4)
            total_calculated = 0.0
            
            for _ in range(num_products):
                product_id = random.randint(1, 14)  # Products 1-14
                quantite = random.randint(1, 3)
                prix_unitaire = round(random.uniform(0.70, 5.0), 2)
                
                sale_line = SaleLine(
                    quantite=quantite,
                    prix_unitaire=prix_unitaire,
                    sale_id=sale.id,
                    product_id=product_id
                )
                db.add(sale_line)
                sale_lines.append(sale_line)
                total_calculated += quantite * prix_unitaire
            
            # Update sale total to match calculated total
            sale.montant_total = round(total_calculated, 2)
        
        db.commit()
        
        # Create some store stocks
        store_stocks = []
        for store_id in range(1, 6):  # Stores 1-5
            for product_id in range(1, 15):  # Products 1-14
                # Not all stores have all products
                if random.random() < 0.8:  # 80% chance store has this product
                    stock = StoreStock(
                        store_id=store_id,
                        product_id=product_id,
                        quantite_stock=random.randint(5, 100),
                        seuil_alerte=random.randint(10, 30)
                    )
                    db.add(stock)
                    store_stocks.append(stock)
        
        db.commit()
        
        # Create central stocks for all products
        central_stocks = []
        for product_id in range(1, 15):  # Products 1-14
            stock = CentralStock(
                product_id=product_id,
                quantite_stock=random.randint(100, 1000),
                seuil_alerte=random.randint(50, 100)
            )
            db.add(stock)
            central_stocks.append(stock)
        
        db.commit()
        
        # Create some restocking requests
        restocking_requests = []
        for _ in range(10):  # 10 sample requests
            store_id = random.randint(1, 5)
            product_id = random.randint(1, 14)
            
            request = RestockingRequest(
                store_id=store_id,
                product_id=product_id,
                quantite_demandee=random.randint(20, 100),
                date_demande=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
                statut=random.choice(["en_attente", "validee", "livree"])
            )
            db.add(request)
            restocking_requests.append(request)
        
        db.commit()
        
        logger.info(f"✅ Reporting database initialized with:")
        logger.info(f"   - {len(sample_sales)} sales")
        logger.info(f"   - {len(sale_lines)} sale lines")
        logger.info(f"   - {len(store_stocks)} store stock entries")
        logger.info(f"   - {len(central_stocks)} central stock entries")
        logger.info(f"   - {len(restocking_requests)} restocking requests") 
    
    except Exception as e:
        logger.error(f"❌ Error initializing Reporting database: {e}")
        db.rollback()
        raise
    
    finally:
        db.close() 