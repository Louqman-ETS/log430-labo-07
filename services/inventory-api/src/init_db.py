from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models import Base, Category, Product, StockMovement, StockAlert
import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialise la base de données avec des données d'exemple"""
    db = SessionLocal()

    try:
        # Vérifier si des données existent déjà
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            logger.info("Database already contains data, skipping initialization")
            return

        logger.info("Initializing database with sample data...")

        # Créer les catégories
        categories = [
            Category(
                nom="Alimentaire", description="Produits alimentaires et boissons"
            ),
            Category(
                nom="Électronique",
                description="Appareils électroniques et informatiques",
            ),
            Category(nom="Vêtements", description="Habillement et accessoires"),
            Category(nom="Maison", description="Articles pour la maison et le jardin"),
            Category(nom="Sport", description="Équipements et vêtements de sport"),
            Category(nom="Loisirs", description="Livres, jeux et divertissements"),
        ]

        for category in categories:
            db.add(category)

        db.commit()
        logger.info(f"✅ Created {len(categories)} categories")

        # Créer les produits
        products = [
            # Alimentaire
            Product(
                code="ALI001",
                nom="Pain complet",
                description="Pain complet bio 500g",
                prix=2.50,
                quantite_stock=50,
                seuil_alerte=10,
                categorie_id=1,
            ),
            Product(
                code="ALI002",
                nom="Lait d'amande",
                description="Lait d'amande bio 1L",
                prix=3.20,
                quantite_stock=30,
                seuil_alerte=5,
                categorie_id=1,
            ),
            Product(
                code="ALI003",
                nom="Pommes bio",
                description="Pommes bio Golden 1kg",
                prix=4.80,
                quantite_stock=25,
                seuil_alerte=8,
                categorie_id=1,
            ),
            # Électronique
            Product(
                code="ELE001",
                nom="Smartphone Galaxy",
                description="Samsung Galaxy S21 128GB",
                prix=699.99,
                quantite_stock=15,
                seuil_alerte=3,
                categorie_id=2,
            ),
            Product(
                code="ELE002",
                nom="Laptop Dell",
                description="Dell Inspiron 15 pouces 8GB RAM",
                prix=899.99,
                quantite_stock=8,
                seuil_alerte=2,
                categorie_id=2,
            ),
            Product(
                code="ELE003",
                nom="Casque Bluetooth",
                description="Sony WH-1000XM4",
                prix=349.99,
                quantite_stock=20,
                seuil_alerte=5,
                categorie_id=2,
            ),
            # Vêtements
            Product(
                code="VET001",
                nom="T-shirt coton",
                description="T-shirt 100% coton bio",
                prix=24.99,
                quantite_stock=100,
                seuil_alerte=20,
                categorie_id=3,
            ),
            Product(
                code="VET002",
                nom="Jeans slim",
                description="Jeans slim fit stretch",
                prix=79.99,
                quantite_stock=45,
                seuil_alerte=10,
                categorie_id=3,
            ),
            Product(
                code="VET003",
                nom="Veste en cuir",
                description="Veste en cuir véritable",
                prix=199.99,
                quantite_stock=12,
                seuil_alerte=3,
                categorie_id=3,
            ),
            # Maison
            Product(
                code="MAI001",
                nom="Cafetière",
                description="Cafetière programmable 12 tasses",
                prix=89.99,
                quantite_stock=18,
                seuil_alerte=5,
                categorie_id=4,
            ),
            Product(
                code="MAI002",
                nom="Oreillers mémoire",
                description="Oreillers mémoire de forme",
                prix=49.99,
                quantite_stock=35,
                seuil_alerte=8,
                categorie_id=4,
            ),
            Product(
                code="MAI003",
                nom="Lampe de bureau",
                description="Lampe LED réglable",
                prix=34.99,
                quantite_stock=22,
                seuil_alerte=6,
                categorie_id=4,
            ),
            # Sport
            Product(
                code="SPO001",
                nom="Ballon de foot",
                description="Ballon de football taille 5",
                prix=29.99,
                quantite_stock=30,
                seuil_alerte=8,
                categorie_id=5,
            ),
            Product(
                code="SPO002",
                nom="Tapis de yoga",
                description="Tapis de yoga antidérapant",
                prix=39.99,
                quantite_stock=25,
                seuil_alerte=6,
                categorie_id=5,
            ),
            Product(
                code="SPO003",
                nom="Dumbbells 5kg",
                description="Haltères en fonte 5kg paire",
                prix=44.99,
                quantite_stock=15,
                seuil_alerte=4,
                categorie_id=5,
            ),
            # Loisirs
            Product(
                code="LOI001",
                nom="Livre thriller",
                description="Thriller best-seller",
                prix=19.99,
                quantite_stock=40,
                seuil_alerte=10,
                categorie_id=6,
            ),
            Product(
                code="LOI002",
                nom="Jeu de société",
                description="Jeu de stratégie familial",
                prix=34.99,
                quantite_stock=20,
                seuil_alerte=5,
                categorie_id=6,
            ),
            Product(
                code="LOI003",
                nom="Puzzle 1000 pièces",
                description="Puzzle paysage montagne",
                prix=24.99,
                quantite_stock=15,
                seuil_alerte=4,
                categorie_id=6,
            ),
        ]

        for product in products:
            db.add(product)

        db.commit()
        logger.info(f"✅ Created {len(products)} products")

        # Créer quelques mouvements de stock pour simuler l'activité
        movements = [
            # Entrées de stock
            StockMovement(
                product_id=1,
                type_mouvement="entree",
                quantite=50,
                raison="Réapprovisionnement initial",
                reference="INIT-001",
            ),
            StockMovement(
                product_id=2,
                type_mouvement="entree",
                quantite=30,
                raison="Réapprovisionnement initial",
                reference="INIT-001",
            ),
            StockMovement(
                product_id=4,
                type_mouvement="entree",
                quantite=15,
                raison="Livraison fournisseur",
                reference="LIV-001",
            ),
            # Sorties de stock (ventes simulées)
            StockMovement(
                product_id=1,
                type_mouvement="sortie",
                quantite=5,
                raison="Vente",
                reference="VENTE-001",
            ),
            StockMovement(
                product_id=7,
                type_mouvement="sortie",
                quantite=10,
                raison="Vente",
                reference="VENTE-002",
            ),
            StockMovement(
                product_id=10,
                type_mouvement="sortie",
                quantite=3,
                raison="Vente",
                reference="VENTE-003",
            ),
        ]

        for movement in movements:
            db.add(movement)

        db.commit()
        logger.info(f"✅ Created {len(movements)} stock movements")

        # Créer quelques alertes de stock
        alerts = [
            StockAlert(
                product_id=5,
                type_alerte="stock_faible",
                message="Stock faible pour Laptop Dell (8 unités)",
            ),
            StockAlert(
                product_id=12,
                type_alerte="stock_faible",
                message="Stock faible pour Veste en cuir (12 unités)",
            ),
        ]

        for alert in alerts:
            db.add(alert)

        db.commit()
        logger.info(f"✅ Created {len(alerts)} stock alerts")

        logger.info("🎉 Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    init_database()
