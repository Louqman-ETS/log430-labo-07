import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Categorie, Produit, Caisse, Vente, LigneVente
from src.service import ProduitService, CategorieService, VenteService
from tests.test_config import test_db


class TestServices(unittest.TestCase):
    """Tests unitaires pour les services métier"""

    def setUp(self):
        """Configure l'environnement de test"""
        test_db.setup()

        # Patcher la session de base de données
        self.session_patcher = patch("src.db.db.get_session", test_db.get_session)
        self.session_patcher.start()

        # Créer une session pour configurer les données de test
        with test_db.get_session() as session:
            # Nettoyer les données existantes
            session.query(LigneVente).delete()
            session.query(Vente).delete()
            session.query(Produit).delete()
            session.query(Categorie).delete()
            session.query(Caisse).delete()
            session.commit()

            # Ajouter des données de test
            # Catégories
            categorie1 = Categorie(
                nom="Alimentaire", description="Produits alimentaires"
            )
            categorie2 = Categorie(nom="Boissons", description="Produits à boire")
            session.add_all([categorie1, categorie2])
            session.commit()

            # Stocker les IDs
            self.categorie1_id = categorie1.id
            self.categorie2_id = categorie2.id

            # Produits
            produit1 = Produit(
                code="ALI001",
                nom="Pain",
                description="Baguette fraîche",
                prix=1.20,
                quantite_stock=50,
                categorie_id=self.categorie1_id,
            )
            produit2 = Produit(
                code="BOI001",
                nom="Eau minérale",
                description="Bouteille 1L",
                prix=0.90,
                quantite_stock=100,
                categorie_id=self.categorie2_id,
            )
            session.add_all([produit1, produit2])
            session.commit()

            # Stocker les IDs
            self.produit1_id = produit1.id
            self.produit2_id = produit2.id

            # Caisse
            caisse = Caisse(numero=1, nom="Caisse principale")
            session.add(caisse)
            session.commit()

            # Stocker l'ID
            self.caisse_id = caisse.id

    def tearDown(self):
        """Nettoie l'environnement après chaque test"""
        self.session_patcher.stop()
        test_db.cleanup()

    def test_produit_service_recherche(self):
        """Test de recherche de produits"""
        # Recherche par nom
        resultats = ProduitService.rechercher_produit("Pain")
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0]["nom"], "Pain")
        self.assertEqual(resultats[0]["prix"], 1.20)
        self.assertEqual(resultats[0]["categorie"], "Alimentaire")

        # Recherche par code
        resultats = ProduitService.rechercher_produit("ALI001")
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0]["code"], "ALI001")

        # Recherche inexistante
        resultats = ProduitService.rechercher_produit("Inexistant")
        self.assertEqual(len(resultats), 0)

    def test_produit_service_recherche_par_categorie(self):
        """Test de recherche de produits par catégorie"""
        # Recherche par nom de catégorie exacte
        resultats = ProduitService.rechercher_par_categorie("Alimentaire")
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0]["nom"], "Pain")

        # Recherche par nom de catégorie partiel (insensible à la casse)
        resultats = ProduitService.rechercher_par_categorie("alimentaire")
        self.assertEqual(len(resultats), 1)

        # Recherche inexistante
        resultats = ProduitService.rechercher_par_categorie("Inexistant")
        self.assertEqual(len(resultats), 0)

    def test_produit_service_details(self):
        """Test de récupération des détails d'un produit"""
        # Produit existant
        produit = ProduitService.get_produit_details(self.produit1_id)
        self.assertIsNotNone(produit)
        self.assertEqual(produit["nom"], "Pain")
        self.assertEqual(produit["description"], "Baguette fraîche")

        # Produit inexistant
        produit = ProduitService.get_produit_details(999)
        self.assertIsNone(produit)

    def test_categorie_service(self):
        """Test de récupération des catégories"""
        categories = CategorieService.liste_categories()
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]["nom"], "Alimentaire")
        self.assertEqual(categories[1]["nom"], "Boissons")

    def test_vente_service_demarrer(self):
        """Test de démarrage d'une vente"""
        # Caisse existante
        vente_id = VenteService.demarrer_vente(self.caisse_id)
        self.assertIsNotNone(vente_id)

        # Caisse inexistante
        vente_id = VenteService.demarrer_vente(999)
        self.assertIsNone(vente_id)

    def test_vente_service_ajouter_produit(self):
        """Test d'ajout de produit à une vente"""
        # Créer une vente
        vente_id = VenteService.demarrer_vente(self.caisse_id)

        # Ajouter un produit existant avec quantité valide
        success, message = VenteService.ajouter_produit(vente_id, self.produit1_id, 2)
        self.assertTrue(success)
        self.assertIn("Pain", message)

        # Ajouter un produit avec quantité excessive
        success, message = VenteService.ajouter_produit(vente_id, self.produit1_id, 100)
        self.assertFalse(success)
        self.assertIn("insuffisant", message)

        # Ajouter un produit inexistant
        success, message = VenteService.ajouter_produit(vente_id, 999)
        self.assertFalse(success)
        self.assertIn("introuvable", message)

    def test_vente_service_finaliser(self):
        """Test de finalisation d'une vente"""
        # Créer une vente avec des produits
        vente_id = VenteService.demarrer_vente(self.caisse_id)
        VenteService.ajouter_produit(vente_id, self.produit1_id, 2)
        VenteService.ajouter_produit(vente_id, self.produit2_id, 1)

        # Finaliser la vente
        success, details = VenteService.finaliser_vente(vente_id)
        self.assertTrue(success)
        self.assertEqual(details["vente_id"], vente_id)
        self.assertEqual(details["caisse"], 1)
        self.assertEqual(details["total"], 3.30)  # 2*1.20 + 1*0.90
        self.assertEqual(len(details["lignes"]), 2)

        # Finaliser une vente inexistante
        success, details = VenteService.finaliser_vente(999)
        self.assertFalse(success)
        self.assertIn("erreur", details)


if __name__ == "__main__":
    unittest.main()
