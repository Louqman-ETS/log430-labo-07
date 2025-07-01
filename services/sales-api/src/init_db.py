from datetime import datetime, timedelta
import random
from .database import SessionLocal, engine, Base
from .models import Sale, SaleLine

def init_database():
    """Initialise la base de données avec des données d'exemple"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Vérifier si des données existent déjà
        if db.query(Sale).first():
            print("✅ Sales database already initialized")
            return
        
        # Créer des ventes d'exemple
        sample_sales = []
        
        # Générer 25 ventes sur les 30 derniers jours
        for i in range(25):
            # Date aléatoire dans les 30 derniers jours
            days_ago = random.randint(0, 30)
            sale_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Store et caisse aléatoires (basés sur les données des autres services)
            store_id = random.randint(1, 5)
            cash_register_id = random.randint(1, 15)
            
            sale = Sale(
                store_id=store_id,
                cash_register_id=cash_register_id,
                date_vente=sale_date,
                total=0.0,  # Sera calculé après les lignes
                notes=f"Vente automatique #{i+1}" if i % 5 == 0 else None
            )
            
            db.add(sale)
            db.flush()  # Pour obtenir l'ID
            
            # Créer 1-4 lignes de vente par vente
            num_lines = random.randint(1, 4)
            total = 0.0
            
            for j in range(num_lines):
                product_id = random.randint(1, 14)  # IDs des produits
                quantity = random.randint(1, 3)
                
                # Prix basés sur les produits réels
                prix_produits = {
                    1: 1.2,   # Pain
                    2: 1.1,   # Lait
                    3: 2.3,   # Oeufs
                    4: 2.5,   # Fromage
                    5: 0.95,  # Pâtes
                    6: 0.7,   # Eau minérale
                    7: 1.9,   # Jus d'orange
                    8: 1.8,   # Soda cola
                    9: 3.5,   # Shampooing
                    10: 1.2,  # Savon
                    11: 2.8,  # Dentifrice
                    12: 2.4,  # Liquide vaisselle
                    13: 1.5,  # Éponges
                    14: 3.2   # Nettoyant multi-usage
                }
                
                prix_unitaire = prix_produits.get(product_id, 2.0)
                sous_total = quantity * prix_unitaire
                total += sous_total
                
                sale_line = SaleLine(
                    sale_id=sale.id,
                    product_id=product_id,
                    quantite=quantity,
                    prix_unitaire=prix_unitaire,
                    sous_total=sous_total
                )
                
                db.add(sale_line)
            
            # Mettre à jour le total de la vente
            sale.total = round(total, 2)
            sample_sales.append(sale)
        
        db.commit()
        print(f"✅ Sales database initialized with {len(sample_sales)} sales")
        
    except Exception as e:
        print(f"❌ Error initializing sales database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 