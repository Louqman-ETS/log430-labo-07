import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Categorie, Produit, Caisse, Vente, LigneVente
from src.dao import ProduitDAO, CategorieDAO, VenteDAO, CaisseDAO

class TestDAO(unittest.TestCase):
    """Tests unitaires pour les objets d'accès aux données (DAO)"""
    
    def setUp(self):
        """Configure l'environnement de test avec une BD en mémoire"""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Créer des données de test
        # 1. Catégories
        self.categorie1 = Categorie(nom="Alimentaire", description="Produits alimentaires")
        self.categorie2 = Categorie(nom="Boissons", description="Produits à boire")
        self.session.add_all([self.categorie1, self.categorie2])
        self.session.commit()
        
        # 2. Produits
        self.produit1 = Produit(
            code="ALI001",
            nom="Pain",
            description="Baguette fraîche",
            prix=1.20,
            quantite_stock=50,
            categorie_id=self.categorie1.id
        )
        self.produit2 = Produit(
            code="ALI002",
            nom="Fromage",
            description="Fromage local",
            prix=3.50,
            quantite_stock=30,
            categorie_id=self.categorie1.id
        )
        self.produit3 = Produit(
            code="BOI001",
            nom="Eau minérale",
            description="Bouteille 1L",
            prix=0.90,
            quantite_stock=100,
            categorie_id=self.categorie2.id
        )
        self.session.add_all([self.produit1, self.produit2, self.produit3])
        
        # 3. Caisse
        self.caisse = Caisse(numero=1, nom="Caisse principale")
        self.session.add(self.caisse)
        self.session.commit()
    
    def tearDown(self):
        """Nettoie l'environnement après les tests"""
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_produit_dao(self):
        """Test des méthodes de ProduitDAO"""
        # Test get_by_id
        produit = ProduitDAO.get_by_id(self.session, self.produit1.id)
        self.assertEqual(produit.nom, "Pain")
        
        # Test get_by_code
        produit = ProduitDAO.get_by_code(self.session, "ALI002")
        self.assertEqual(produit.nom, "Fromage")
        
        # Test search_by_name
        produits = ProduitDAO.search_by_name(self.session, "a")
        self.assertEqual(len(produits), 3)  # Pain, Fromage, Eau minérale
        
        produits = ProduitDAO.search_by_name(self.session, "Eau")
        self.assertEqual(len(produits), 1)
        
        # Test search_by_category
        produits = ProduitDAO.search_by_category(self.session, self.categorie1.id)
        self.assertEqual(len(produits), 2)  # Pain, Fromage
        
        # Test search (général)
        produits = ProduitDAO.search(self.session, "ALI")
        self.assertEqual(len(produits), 2)  # ALI001, ALI002
        
        # Test update_stock
        result = ProduitDAO.update_stock(self.session, self.produit1.id, -10)
        self.assertTrue(result)
        produit = ProduitDAO.get_by_id(self.session, self.produit1.id)
        self.assertEqual(produit.quantite_stock, 40)  # 50 - 10
        
        # Test update_stock avec quantité insuffisante
        result = ProduitDAO.update_stock(self.session, self.produit1.id, -50)
        self.assertFalse(result)
    
    def test_categorie_dao(self):
        """Test des méthodes de CategorieDAO"""
        # Test get_all
        categories = CategorieDAO.get_all(self.session)
        self.assertEqual(len(categories), 2)
        
        # Test get_by_id
        categorie = CategorieDAO.get_by_id(self.session, self.categorie1.id)
        self.assertEqual(categorie.nom, "Alimentaire")
        
        # Test get_by_name (exact)
        categorie = CategorieDAO.get_by_name(self.session, "Boissons")
        self.assertEqual(categorie.description, "Produits à boire")
        
        # Test get_by_name (partiel)
        categorie = CategorieDAO.get_by_name(self.session, "aliment")
        self.assertEqual(categorie.nom, "Alimentaire")
    
    def test_vente_dao(self):
        """Test des méthodes de VenteDAO"""
        # Test create_vente
        vente = VenteDAO.create_vente(self.session, self.caisse.id)
        self.assertIsNotNone(vente.id)
        self.assertEqual(vente.montant_total, 0)
        self.assertEqual(vente.caisse_id, self.caisse.id)
        
        # Test add_product_to_vente
        ligne = VenteDAO.add_product_to_vente(self.session, vente.id, self.produit1.id, 2)
        self.assertIsNotNone(ligne)
        
        # Vérifier que le stock a été mis à jour
        produit = ProduitDAO.get_by_id(self.session, self.produit1.id)
        self.assertEqual(produit.quantite_stock, 48)  # 50 - 2
        
        # Vérifier que le montant de la vente a été mis à jour
        vente = VenteDAO.get_vente(self.session, vente.id)
        self.assertEqual(vente.montant_total, 2.40)  # 2 * 1.20
        
        # Test get_vente_with_lignes
        vente_lignes = VenteDAO.get_vente_with_lignes(self.session, vente.id)
        self.assertIsNotNone(vente_lignes)
        self.assertEqual(len(vente_lignes[1]), 1)  # Une seule ligne de vente
        
        # Test supprimer_vente
        result = VenteDAO.supprimer_vente(self.session, vente.id)
        self.assertTrue(result)
        
        # Vérifier que les produits ont été remis en stock
        produit = ProduitDAO.get_by_id(self.session, self.produit1.id)
        self.assertEqual(produit.quantite_stock, 50)  # Retour au stock initial
        
        # Vérifier que la vente a été supprimée
        vente = VenteDAO.get_vente(self.session, vente.id)
        self.assertIsNone(vente)

    def test_caisse_dao(self):
        """Test des méthodes de CaisseDAO"""
        # Test get_all
        caisses = CaisseDAO.get_all(self.session)
        self.assertEqual(len(caisses), 1)
        
        # Test get_by_id
        caisse = CaisseDAO.get_by_id(self.session, self.caisse.id)
        self.assertEqual(caisse.numero, 1)
        self.assertEqual(caisse.nom, "Caisse principale")

if __name__ == '__main__':
    unittest.main() 