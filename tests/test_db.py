import unittest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.db import Base
from src.models import Categorie, Produit, Caisse, Vente, LigneVente  # Import des modèles
from tests.test_config import setup_test_database, cleanup_test_database, get_test_session


class TestDBConfig(unittest.TestCase):
    """Tests pour la configuration de la base de données"""

    @classmethod
    def setUpClass(cls):
        """Configuration une seule fois pour toute la classe"""
        cls.engine = setup_test_database()

    @classmethod
    def tearDownClass(cls):
        """Nettoyage une seule fois après tous les tests"""
        cleanup_test_database(cls.engine)

    def test_base_metadata(self):
        """Vérifie que les métadonnées de Base sont correctement configurées"""
        # Vérifier que la classe Base possède des métadonnées
        self.assertTrue(hasattr(Base, "metadata"))

        # Vérifier la présence des tables dans les métadonnées
        tables = Base.metadata.tables
        expected_tables = {
            "categories",
            "produits",
            "caisses",
            "ventes",
            "lignes_vente",
        }
        for table in expected_tables:
            self.assertIn(table, tables, f"Table '{table}' not found in metadata")

    def test_db_connection(self):
        """Vérifie que la connexion à la base de données fonctionne"""
        # Vérifier que la connexion fonctionne et que les tables existent
        with self.engine.connect() as conn:
            # Vérifier que les tables ont été créées (PostgreSQL)
            result = conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            )
            tables = [row[0] for row in result]

            # Vérifier la présence des tables principales
            self.assertIn("categories", tables)
            self.assertIn("produits", tables)
            self.assertIn("caisses", tables)
            self.assertIn("ventes", tables)
            self.assertIn("lignes_vente", tables)

    def test_session_creation(self):
        """Vérifie que la création de session fonctionne"""
        session = get_test_session(self.engine)
        self.assertIsNotNone(session)
        session.close()


if __name__ == "__main__":
    unittest.main()
