from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models import Base, Store, CashRegister, Sale, SaleLine
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with sample data if empty"""
    db = SessionLocal()

    try:
        # Vérifier si des données existent déjà
        existing_stores = db.query(Store).count()
        if existing_stores > 0:
            logger.info("📊 Database already contains data, skipping initialization")
            return

        logger.info("🏪 Initializing retail database with sample data...")

        # Créer les magasins
        stores = [
            Store(
                nom="Magasin Centre-Ville",
                adresse="123 Rue Principale, Montréal, QC",
                telephone="(514) 555-0101",
                email="centreville@retail.com",
            ),
            Store(
                nom="Magasin Westmount",
                adresse="456 Avenue Sherbrooke, Westmount, QC",
                telephone="(514) 555-0202",
                email="westmount@retail.com",
            ),
            Store(
                nom="Magasin Laval",
                adresse="789 Boulevard des Laurentides, Laval, QC",
                telephone="(450) 555-0303",
                email="laval@retail.com",
            ),
            Store(
                nom="Magasin Brossard",
                adresse="321 Boulevard Taschereau, Brossard, QC",
                telephone="(450) 555-0404",
                email="brossard@retail.com",
            ),
            Store(
                nom="Magasin Longueuil",
                adresse="654 Rue Saint-Charles, Longueuil, QC",
                telephone="(450) 555-0505",
                email="longueuil@retail.com",
            ),
        ]

        for store in stores:
            db.add(store)

        db.commit()
        logger.info(f"✅ Created {len(stores)} stores")

        # Créer les caisses enregistreuses pour chaque magasin
        cash_registers = []
        for store in stores:
            for i in range(1, 4):  # 3 caisses par magasin
                cash_register = CashRegister(
                    numero=i, nom=f"Caisse {i}", store_id=store.id
                )
                cash_registers.append(cash_register)
                db.add(cash_register)

        db.commit()
        logger.info(f"✅ Created {len(cash_registers)} cash registers")

        # Créer des ventes d'exemple
        sample_sales = [
            # Magasin Centre-Ville
            {
                "store_id": 1,
                "cash_register_id": 1,
                "total": 125.50,
                "notes": "Vente normale",
                "lines": [
                    {
                        "product_id": 1,
                        "quantite": 2,
                        "prix_unitaire": 25.00,
                        "sous_total": 50.00,
                    },
                    {
                        "product_id": 3,
                        "quantite": 1,
                        "prix_unitaire": 75.50,
                        "sous_total": 75.50,
                    },
                ],
            },
            {
                "store_id": 1,
                "cash_register_id": 2,
                "total": 89.99,
                "notes": "Vente avec promotion",
                "lines": [
                    {
                        "product_id": 2,
                        "quantite": 1,
                        "prix_unitaire": 89.99,
                        "sous_total": 89.99,
                    }
                ],
            },
            # Magasin Westmount
            {
                "store_id": 2,
                "cash_register_id": 4,
                "total": 245.75,
                "notes": "Vente premium",
                "lines": [
                    {
                        "product_id": 4,
                        "quantite": 1,
                        "prix_unitaire": 199.99,
                        "sous_total": 199.99,
                    },
                    {
                        "product_id": 5,
                        "quantite": 2,
                        "prix_unitaire": 22.88,
                        "sous_total": 45.76,
                    },
                ],
            },
            {
                "store_id": 2,
                "cash_register_id": 5,
                "total": 156.25,
                "notes": "Vente standard",
                "lines": [
                    {
                        "product_id": 1,
                        "quantite": 3,
                        "prix_unitaire": 25.00,
                        "sous_total": 75.00,
                    },
                    {
                        "product_id": 6,
                        "quantite": 1,
                        "prix_unitaire": 81.25,
                        "sous_total": 81.25,
                    },
                ],
            },
            # Magasin Laval
            {
                "store_id": 3,
                "cash_register_id": 7,
                "total": 67.50,
                "notes": "Vente rapide",
                "lines": [
                    {
                        "product_id": 7,
                        "quantite": 3,
                        "prix_unitaire": 22.50,
                        "sous_total": 67.50,
                    }
                ],
            },
            {
                "store_id": 3,
                "cash_register_id": 8,
                "total": 189.99,
                "notes": "Vente avec service",
                "lines": [
                    {
                        "product_id": 8,
                        "quantite": 1,
                        "prix_unitaire": 189.99,
                        "sous_total": 189.99,
                    }
                ],
            },
            # Magasin Brossard
            {
                "store_id": 4,
                "cash_register_id": 10,
                "total": 134.75,
                "notes": "Vente familiale",
                "lines": [
                    {
                        "product_id": 9,
                        "quantite": 2,
                        "prix_unitaire": 45.00,
                        "sous_total": 90.00,
                    },
                    {
                        "product_id": 10,
                        "quantite": 1,
                        "prix_unitaire": 44.75,
                        "sous_total": 44.75,
                    },
                ],
            },
            # Magasin Longueuil
            {
                "store_id": 5,
                "cash_register_id": 13,
                "total": 299.99,
                "notes": "Vente importante",
                "lines": [
                    {
                        "product_id": 11,
                        "quantite": 1,
                        "prix_unitaire": 299.99,
                        "sous_total": 299.99,
                    }
                ],
            },
            {
                "store_id": 5,
                "cash_register_id": 14,
                "total": 78.25,
                "notes": "Vente quotidienne",
                "lines": [
                    {
                        "product_id": 12,
                        "quantite": 1,
                        "prix_unitaire": 78.25,
                        "sous_total": 78.25,
                    }
                ],
            },
        ]

        for sale_data in sample_sales:
            # Créer la vente
            sale = Sale(
                store_id=sale_data["store_id"],
                cash_register_id=sale_data["cash_register_id"],
                total=sale_data["total"],
                notes=sale_data["notes"],
            )
            db.add(sale)
            db.flush()  # Pour obtenir l'ID de la vente

            # Créer les lignes de vente
            for line_data in sale_data["lines"]:
                line = SaleLine(
                    sale_id=sale.id,
                    product_id=line_data["product_id"],
                    quantite=line_data["quantite"],
                    prix_unitaire=line_data["prix_unitaire"],
                    sous_total=line_data["sous_total"],
                )
                db.add(line)

        db.commit()
        logger.info(f"✅ Created {len(sample_sales)} sample sales")

        logger.info("🎉 Retail database initialization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    init_database()
