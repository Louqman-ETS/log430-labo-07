import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.models import Base, Categorie, Produit, Caisse, Vente, LigneVente


class TestModels(unittest.TestCase):
    """Tests unitaires pour les modèles de données"""

    def setUp(self):
        """Configure l'environnement de test avec une BD en mémoire"""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Créer des données de base pour les tests
        self.categorie = Categorie(
            nom="Test Catégorie", description="Description de test"
        )
        self.session.add(self.categorie)
        self.session.commit()

        self.produit = Produit(
            code="TEST123",
            nom="Produit Test",
            description="Description du produit test",
            prix=10.99,
            quantite_stock=20,
            categorie_id=self.categorie.id,
        )
        self.session.add(self.produit)

        self.caisse = Caisse(numero=1, nom="Caisse Test")
        self.session.add(self.caisse)
        self.session.commit()

    def tearDown(self):
        """Nettoie l'environnement après les tests"""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_categorie(self):
        """Test du modèle Categorie"""
        categorie = (
            self.session.query(Categorie).filter_by(nom="Test Catégorie").first()
        )
        self.assertIsNotNone(categorie)
        self.assertEqual(categorie.nom, "Test Catégorie")
        self.assertEqual(categorie.description, "Description de test")

    def test_produit(self):
        """Test du modèle Produit"""
        produit = self.session.query(Produit).filter_by(code="TEST123").first()
        self.assertIsNotNone(produit)
        self.assertEqual(produit.nom, "Produit Test")
        self.assertEqual(produit.prix, 10.99)
        self.assertEqual(produit.quantite_stock, 20)
        self.assertEqual(produit.categorie.nom, "Test Catégorie")

    def test_caisse(self):
        """Test du modèle Caisse"""
        caisse = self.session.query(Caisse).filter_by(numero=1).first()
        self.assertIsNotNone(caisse)
        self.assertEqual(caisse.nom, "Caisse Test")

    def test_vente_et_lignes(self):
        """Test des modèles Vente et LigneVente"""
        # Créer une vente
        vente = Vente(caisse_id=self.caisse.id)
        self.session.add(vente)
        self.session.commit()

        # Vérifier la vente
        self.assertIsNotNone(vente.id)
        self.assertIsInstance(vente.date_heure, datetime)
        self.assertEqual(vente.montant_total, 0)

        # Ajouter une ligne de vente
        ligne = LigneVente(
            vente_id=vente.id,
            produit_id=self.produit.id,
            quantite=2,
            prix_unitaire=self.produit.prix,
        )
        self.session.add(ligne)

        # Mettre à jour le montant total (comme le ferait le DAO)
        vente.montant_total = ligne.quantite * ligne.prix_unitaire
        self.session.commit()

        # Vérifier la ligne et les relations
        self.assertEqual(ligne.vente_id, vente.id)
        self.assertEqual(ligne.produit_id, self.produit.id)
        self.assertEqual(ligne.quantite, 2)
        self.assertEqual(ligne.prix_unitaire, 10.99)
        self.assertEqual(vente.montant_total, 21.98)

        # Vérifier les relations
        self.assertEqual(len(vente.lignes), 1)
        self.assertEqual(vente.lignes[0].produit.nom, "Produit Test")


if __name__ == "__main__":
    unittest.main()
