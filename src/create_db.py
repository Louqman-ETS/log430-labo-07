import os
from sqlalchemy.orm import Session
import sqlite3  # ou votre système de base de données

from src.db import engine, Base, SessionLocal
from src.models import Categorie, Produit, Caisse


def ensure_data_directory():
    if not os.path.exists("data"):
        os.makedirs("data")


def initialize_db():
    """Initialise la base de données et crée les tables"""
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)

    # Créer les tables seulement si elles n'existent pas
    Base.metadata.create_all(bind=engine)


def initialize_data():
    """Initialise les données de base si la base de données est vide"""
    db = SessionLocal()
    try:
        # Vérifier si des données existent déjà
        if db.query(Categorie).first() is not None:
            print("La base de données contient déjà des données.")
            return

        # Si pas de données, on initialise
        categories = [
            Categorie(nom="Alimentaire", description="Produits alimentaires"),
            Categorie(nom="Boissons", description="Boissons diverses"),
            Categorie(nom="Hygiène", description="Produits d'hygiène personnelle"),
            Categorie(nom="Ménage", description="Produits d'entretien ménager"),
        ]
        db.add_all(categories)
        db.commit()

        categories = db.query(Categorie).all()
        cat_dict = {cat.nom: cat for cat in categories}

        produits = [
            Produit(
                code="ALI001",
                nom="Pain",
                description="Baguette tradition",
                prix=1.20,
                quantite_stock=50,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI002",
                nom="Lait",
                description="Lait demi-écrémé 1L",
                prix=1.10,
                quantite_stock=40,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI003",
                nom="Oeufs",
                description="Boîte de 6 oeufs bio",
                prix=2.30,
                quantite_stock=30,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI004",
                nom="Fromage",
                description="Emmental râpé 200g",
                prix=2.50,
                quantite_stock=25,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI005",
                nom="Pâtes",
                description="Spaghetti 500g",
                prix=0.95,
                quantite_stock=60,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI006",
                nom="Riz",
                description="Riz basmati 1kg",
                prix=2.75,
                quantite_stock=45,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI007",
                nom="Chocolat",
                description="Tablette noir 70% 100g",
                prix=1.85,
                quantite_stock=35,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="ALI008",
                nom="Céréales",
                description="Flocons d'avoine 500g",
                prix=2.20,
                quantite_stock=28,
                categorie=cat_dict["Alimentaire"],
            ),
            Produit(
                code="BOI001",
                nom="Eau minérale",
                description="Bouteille 1.5L",
                prix=0.70,
                quantite_stock=100,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="BOI002",
                nom="Jus d'orange",
                description="Pur jus 1L",
                prix=1.90,
                quantite_stock=35,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="BOI003",
                nom="Soda cola",
                description="Bouteille 2L",
                prix=1.80,
                quantite_stock=45,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="BOI004",
                nom="Thé vert",
                description="Boîte de 20 sachets",
                prix=2.40,
                quantite_stock=30,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="BOI005",
                nom="Café",
                description="Café moulu 250g",
                prix=3.60,
                quantite_stock=25,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="BOI006",
                nom="Jus de pomme",
                description="Pur jus 1L",
                prix=1.85,
                quantite_stock=32,
                categorie=cat_dict["Boissons"],
            ),
            Produit(
                code="HYG001",
                nom="Shampooing",
                description="Flacon 250ml",
                prix=3.50,
                quantite_stock=20,
                categorie=cat_dict["Hygiène"],
            ),
            Produit(
                code="HYG002",
                nom="Savon",
                description="Pain de savon 100g",
                prix=1.20,
                quantite_stock=40,
                categorie=cat_dict["Hygiène"],
            ),
            Produit(
                code="HYG003",
                nom="Dentifrice",
                description="Tube 75ml",
                prix=2.80,
                quantite_stock=30,
                categorie=cat_dict["Hygiène"],
            ),
            Produit(
                code="HYG004",
                nom="Gel douche",
                description="Flacon 300ml",
                prix=2.95,
                quantite_stock=25,
                categorie=cat_dict["Hygiène"],
            ),
            Produit(
                code="HYG005",
                nom="Déodorant",
                description="Roll-on 50ml",
                prix=2.60,
                quantite_stock=22,
                categorie=cat_dict["Hygiène"],
            ),
            Produit(
                code="MEN001",
                nom="Liquide vaisselle",
                description="Flacon 500ml",
                prix=2.10,
                quantite_stock=25,
                categorie=cat_dict["Ménage"],
            ),
            Produit(
                code="MEN002",
                nom="Nettoyant sol",
                description="Bouteille 1L",
                prix=3.20,
                quantite_stock=20,
                categorie=cat_dict["Ménage"],
            ),
            Produit(
                code="MEN003",
                nom="Lessive",
                description="Paquet 30 lavages",
                prix=7.50,
                quantite_stock=15,
                categorie=cat_dict["Ménage"],
            ),
            Produit(
                code="MEN004",
                nom="Éponges",
                description="Lot de 3",
                prix=1.40,
                quantite_stock=35,
                categorie=cat_dict["Ménage"],
            ),
            Produit(
                code="MEN005",
                nom="Sacs poubelle",
                description="Rouleau de 20 sacs 30L",
                prix=2.30,
                quantite_stock=28,
                categorie=cat_dict["Ménage"],
            ),
        ]
        db.add_all(produits)

        caisses = [
            Caisse(numero=1, nom="Caisse 1"),
            Caisse(numero=2, nom="Caisse 2"),
            Caisse(numero=3, nom="Caisse 3"),
        ]
        db.add_all(caisses)

        db.commit()
        print("Base de données initialisée avec succès.")
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    initialize_db()
    initialize_data()
