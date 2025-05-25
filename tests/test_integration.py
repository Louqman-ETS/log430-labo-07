import unittest
import os
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.db import Base
from src.models import Categorie, Produit, Caisse, Vente, LigneVente
from src.dao import ProduitDAO, CategorieDAO, VenteDAO, CaisseDAO
from src.service import ProduitService, CategorieService, VenteService


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour le système de caisse"""

    def setUp(self):
        """Configuration pour chaque test"""
        # Créer une base de données temporaire en mémoire
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Créer des données de test
        # 1. Catégories
        self.categorie_alim = Categorie(
            nom="Alimentaire", description="Produits alimentaires"
        )
        self.categorie_boisson = Categorie(
            nom="Boissons", description="Boissons diverses"
        )
        self.session.add_all([self.categorie_alim, self.categorie_boisson])
        self.session.commit()

        # 2. Produits
        self.pain = Produit(
            code="A001",
            nom="Pain",
            description="Baguette",
            prix=1.20,
            quantite_stock=50,
            categorie_id=self.categorie_alim.id,
        )
        self.eau = Produit(
            code="B001",
            nom="Eau minérale",
            description="Bouteille 1L",
            prix=0.80,
            quantite_stock=100,
            categorie_id=self.categorie_boisson.id,
        )
        self.session.add_all([self.pain, self.eau])

        # 3. Caisse
        self.caisse = Caisse(numero=1, nom="Caisse test")
        self.session.add(self.caisse)
        self.session.commit()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.session.close()

    def test_dao_integration(self):
        """Test d'intégration des DAOs"""
        # Vérifier que les catégories ont été créées
        categories = CategorieDAO.get_all(self.session)
        self.assertEqual(len(categories), 2)

        # Vérifier que les produits peuvent être recherchés
        produit = ProduitDAO.get_by_code(self.session, "A001")
        self.assertEqual(produit.nom, "Pain")

        produits_alim = ProduitDAO.search_by_category(
            self.session, self.categorie_alim.id
        )
        self.assertEqual(len(produits_alim), 1)

        # Test d'une vente complète
        vente = VenteDAO.create_vente(self.session, self.caisse.id)
        self.assertIsNotNone(vente.id)

        # Ajouter des produits à la vente
        ligne1 = VenteDAO.add_product_to_vente(self.session, vente.id, self.pain.id, 2)
        self.assertIsNotNone(ligne1)

        # Vérifier le stock et le montant total
        pain_apres = ProduitDAO.get_by_id(self.session, self.pain.id)
        self.assertEqual(pain_apres.quantite_stock, 48)  # 50 - 2

        vente_apres = VenteDAO.get_vente(self.session, vente.id)
        self.assertEqual(vente_apres.montant_total, 2.40)  # 2 * 1.20

        # Tester le retour de produit
        result = VenteDAO.supprimer_vente(self.session, vente.id)
        self.assertTrue(result)

        # Vérifier que le stock est revenu à l'état initial
        pain_final = ProduitDAO.get_by_id(self.session, self.pain.id)
        self.assertEqual(pain_final.quantite_stock, 50)

        # Vérifier que la vente a été supprimée
        vente_supprimee = VenteDAO.get_vente(self.session, vente.id)
        self.assertIsNone(vente_supprimee)

    def test_ventes_multiples(self):
        """Test d'intégration avec plusieurs ventes simultanées"""
        # Créer deux ventes
        vente1 = VenteDAO.create_vente(self.session, self.caisse.id)
        vente2 = VenteDAO.create_vente(self.session, self.caisse.id)

        # Ajouter le même produit dans les deux ventes
        ligne1 = VenteDAO.add_product_to_vente(self.session, vente1.id, self.eau.id, 5)
        self.assertIsNotNone(ligne1)

        ligne2 = VenteDAO.add_product_to_vente(self.session, vente2.id, self.eau.id, 10)
        self.assertIsNotNone(ligne2)

        # Vérifier que le stock a été mis à jour correctement
        eau_apres = ProduitDAO.get_by_id(self.session, self.eau.id)
        self.assertEqual(eau_apres.quantite_stock, 85)  # 100 - 5 - 10

        # Vérifier les montants des ventes
        vente1_apres = VenteDAO.get_vente(self.session, vente1.id)
        vente2_apres = VenteDAO.get_vente(self.session, vente2.id)

        self.assertEqual(vente1_apres.montant_total, 4.0)  # 5 * 0.80
        self.assertEqual(vente2_apres.montant_total, 8.0)  # 10 * 0.80


if __name__ == "__main__":
    unittest.main()
