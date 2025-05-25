import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Categorie, Produit, Caisse, Vente, LigneVente
from src.service import ProduitService, CategorieService, VenteService, get_db_session
from src.db import SessionLocal


class TestServices(unittest.TestCase):
    """Tests unitaires pour les services métier"""

    def setUp(self):
        """Configure l'environnement de test"""
        # Créer une base de données en mémoire
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionMock = sessionmaker(bind=self.engine)

        # Patcher la SessionLocal utilisée par get_db_session
        self.session_patcher = patch("src.service.SessionLocal", self.SessionMock)
        self.session_patcher.start()

        # Créer une session pour configurer les données de test
        self.session = self.SessionMock()

        # Ajouter des données de test
        # Catégories
        self.categorie1 = Categorie(
            nom="Alimentaire", description="Produits alimentaires"
        )
        self.categorie2 = Categorie(nom="Boissons", description="Produits à boire")
        self.session.add_all([self.categorie1, self.categorie2])
        self.session.commit()

        # Produits
        self.produit1 = Produit(
            code="ALI001",
            nom="Pain",
            description="Baguette fraîche",
            prix=1.20,
            quantite_stock=50,
            categorie_id=self.categorie1.id,
        )
        self.produit2 = Produit(
            code="BOI001",
            nom="Eau minérale",
            description="Bouteille 1L",
            prix=0.90,
            quantite_stock=100,
            categorie_id=self.categorie2.id,
        )
        self.session.add_all([self.produit1, self.produit2])

        # Caisse
        self.caisse = Caisse(numero=1, nom="Caisse principale")
        self.session.add(self.caisse)
        self.session.commit()

    def tearDown(self):
        """Nettoie l'environnement après les tests"""
        self.session.close()
        self.session_patcher.stop()
        Base.metadata.drop_all(self.engine)

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
        produit = ProduitService.get_produit_details(self.produit1.id)
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
        vente_id = VenteService.demarrer_vente(self.caisse.id)
        self.assertIsNotNone(vente_id)

        # Caisse inexistante
        vente_id = VenteService.demarrer_vente(999)
        self.assertIsNone(vente_id)

    def test_vente_service_ajouter_produit(self):
        """Test d'ajout de produit à une vente"""
        # Créer une vente
        vente_id = VenteService.demarrer_vente(self.caisse.id)

        # Ajouter un produit existant avec quantité valide
        success, message = VenteService.ajouter_produit(vente_id, self.produit1.id, 2)
        self.assertTrue(success)
        self.assertIn("Pain", message)

        # Ajouter un produit avec quantité excessive
        success, message = VenteService.ajouter_produit(vente_id, self.produit1.id, 100)
        self.assertFalse(success)
        self.assertIn("insuffisant", message)

        # Ajouter un produit inexistant
        success, message = VenteService.ajouter_produit(vente_id, 999)
        self.assertFalse(success)
        self.assertIn("introuvable", message)

    def test_vente_service_finaliser(self):
        """Test de finalisation d'une vente"""
        # Créer une vente avec des produits
        vente_id = VenteService.demarrer_vente(self.caisse.id)
        VenteService.ajouter_produit(vente_id, self.produit1.id, 2)
        VenteService.ajouter_produit(vente_id, self.produit2.id, 1)

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
