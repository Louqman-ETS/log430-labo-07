#!/usr/bin/env python3
"""
Script d'initialisation complète de la base de données
Usage: python -m src.create_db
"""

import os
import sys
import random

# Ajouter le répertoire racine au path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app import create_app, db
from src.app.models.models import (
    Magasin,
    Categorie,
    Produit,
    Caisse,
    StockMagasin,
    StockCentral,
)


def main():
    """Fonction principale pour initialiser complètement la base de données"""

    print("🚀 Réinitialisation complète de la base de données...")

    app = create_app()

    with app.app_context():
        try:
            print("🔄 Suppression de toutes les tables existantes...")
            db.drop_all()

            print("🏗️  Création de nouvelles tables...")
            db.create_all()
            print("✅ Structure de base de données créée")

            # === 1. CRÉATION DES MAGASINS ===
            print("\n🏪 Création des magasins...")
            magasins_data = [
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

            for mag_data in magasins_data:
                magasin = Magasin(**mag_data)
                db.session.add(magasin)

            db.session.commit()
            print(f"✅ {len(magasins_data)} magasins créés")

            # === 2. CRÉATION DES CATÉGORIES ===
            print("\n📋 Création des catégories...")
            categories_data = [
                {"nom": "Alimentaire", "description": "Produits alimentaires de base"},
                {"nom": "Boissons", "description": "Boissons diverses"},
                {"nom": "Hygiène", "description": "Produits d'hygiène personnelle"},
                {"nom": "Ménage", "description": "Produits d'entretien ménager"},
            ]

            for cat_data in categories_data:
                categorie = Categorie(**cat_data)
                db.session.add(categorie)

            db.session.commit()
            print(f"✅ {len(categories_data)} catégories créées")

            # === 3. CRÉATION DES CAISSES ===
            print("\n💰 Création des caisses...")
            magasins = Magasin.query.all()

            for magasin in magasins:
                # 3 caisses par magasin
                for i in range(1, 4):
                    caisse = Caisse(numero=i, nom=f"Caisse {i}", magasin_id=magasin.id)
                    db.session.add(caisse)

            db.session.commit()
            nb_caisses = Caisse.query.count()
            print(f"✅ {nb_caisses} caisses créées (3 par magasin)")

            # === 4. CRÉATION DES PRODUITS ===
            print("\n📦 Création des produits...")

            # Récupérer les catégories
            categories = {cat.nom: cat for cat in Categorie.query.all()}

            produits_data = [
                # Alimentaire
                {
                    "code": "ALI001",
                    "nom": "Pain",
                    "description": "Baguette tradition",
                    "prix": 1.20,
                    "categorie": "Alimentaire",
                },
                {
                    "code": "ALI002",
                    "nom": "Lait",
                    "description": "Lait demi-écrémé 1L",
                    "prix": 1.10,
                    "categorie": "Alimentaire",
                },
                {
                    "code": "ALI003",
                    "nom": "Oeufs",
                    "description": "Boîte de 6 oeufs",
                    "prix": 2.30,
                    "categorie": "Alimentaire",
                },
                {
                    "code": "ALI004",
                    "nom": "Fromage",
                    "description": "Emmental râpé 200g",
                    "prix": 2.50,
                    "categorie": "Alimentaire",
                },
                {
                    "code": "ALI005",
                    "nom": "Pâtes",
                    "description": "Spaghetti 500g",
                    "prix": 0.95,
                    "categorie": "Alimentaire",
                },
                # Boissons
                {
                    "code": "BOI001",
                    "nom": "Eau minérale",
                    "description": "Bouteille 1.5L",
                    "prix": 0.70,
                    "categorie": "Boissons",
                },
                {
                    "code": "BOI002",
                    "nom": "Jus d'orange",
                    "description": "Pur jus 1L",
                    "prix": 1.90,
                    "categorie": "Boissons",
                },
                {
                    "code": "BOI003",
                    "nom": "Soda cola",
                    "description": "Bouteille 2L",
                    "prix": 1.80,
                    "categorie": "Boissons",
                },
                # Hygiène
                {
                    "code": "HYG001",
                    "nom": "Shampooing",
                    "description": "Flacon 250ml",
                    "prix": 3.50,
                    "categorie": "Hygiène",
                },
                {
                    "code": "HYG002",
                    "nom": "Savon",
                    "description": "Pain de savon 100g",
                    "prix": 1.20,
                    "categorie": "Hygiène",
                },
                {
                    "code": "HYG003",
                    "nom": "Dentifrice",
                    "description": "Tube 75ml",
                    "prix": 2.80,
                    "categorie": "Hygiène",
                },
                # Ménage
                {
                    "code": "MEN001",
                    "nom": "Liquide vaisselle",
                    "description": "Flacon 500ml",
                    "prix": 2.10,
                    "categorie": "Ménage",
                },
                {
                    "code": "MEN002",
                    "nom": "Nettoyant sol",
                    "description": "Bouteille 1L",
                    "prix": 3.20,
                    "categorie": "Ménage",
                },
            ]

            for prod_data in produits_data:
                categorie = categories[prod_data["categorie"]]
                produit = Produit(
                    code=prod_data["code"],
                    nom=prod_data["nom"],
                    description=prod_data["description"],
                    prix=prod_data["prix"],
                    quantite_stock=0,  # Stock global initialisé à 0
                    categorie_id=categorie.id,
                )
                db.session.add(produit)

            db.session.commit()
            print(f"✅ {len(produits_data)} produits créés")

            # === 5. CRÉATION DES STOCKS MAGASIN ===
            print("\n📦 Création des stocks par magasin...")
            produits = Produit.query.all()

            for magasin in magasins:
                for produit in produits:
                    # Stock initial aléatoire entre 20 et 100
                    stock_initial = random.randint(20, 100)

                    stock = StockMagasin(
                        magasin_id=magasin.id,
                        produit_id=produit.id,
                        quantite_stock=stock_initial,
                        seuil_alerte=random.randint(10, 20),
                    )
                    db.session.add(stock)

            db.session.commit()
            nb_stocks = StockMagasin.query.count()
            print(f"✅ {nb_stocks} stocks magasin créés")

            # === 6. CRÉATION DU STOCK CENTRAL ===
            print("\n🏭 Création du stock central...")

            for produit in produits:
                # Stock central entre 500 et 2000
                stock_central = random.randint(500, 2000)

                stock = StockCentral(
                    produit_id=produit.id,
                    quantite_stock=stock_central,
                    seuil_alerte=random.randint(100, 200),
                )
                db.session.add(stock)

            db.session.commit()
            nb_stocks_central = StockCentral.query.count()
            print(f"✅ {nb_stocks_central} stocks centraux créés")

            # === RÉSUMÉ FINAL ===
            print("\n" + "=" * 50)
            print("📊 RÉSUMÉ DE L'INITIALISATION")
            print("=" * 50)
            print(f"   🏪 Magasins: {Magasin.query.count()}")
            print(f"   💰 Caisses: {Caisse.query.count()}")
            print(f"   📋 Catégories: {Categorie.query.count()}")
            print(f"   📦 Produits: {Produit.query.count()}")
            print(f"   🏬 Stocks magasin: {StockMagasin.query.count()}")
            print(f"   🏭 Stocks central: {StockCentral.query.count()}")
            print("=" * 50)

            print("\n✅ Base de données complètement initialisée !")
            print("🌐 Application prête à utiliser sur http://localhost:8081")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")
            import traceback

            traceback.print_exc()
            return False

    return True


if __name__ == "__main__":
    main()
