import unittest
import tempfile
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.db import Base, engine


class TestDBConfig(unittest.TestCase):
    """Tests pour la configuration de la base de données"""

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
            self.assertIn(table, tables)

    def test_db_connection(self):
        """Vérifie que la connexion à la base de données fonctionne"""
        # Créer une base de données temporaire
        db_fd, db_path = tempfile.mkstemp()

        try:
            # Créer un moteur pour cette base
            engine = create_engine(f"sqlite:///{db_path}")

            # Créer les tables
            Base.metadata.create_all(engine)

            # Vérifier que la connexion fonctionne et que les tables existent
            with engine.connect() as conn:
                # Vérifier que les tables ont été créées
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result]

                # Vérifier la présence des tables principales
                self.assertIn("categories", tables)
                self.assertIn("produits", tables)
                self.assertIn("caisses", tables)
                self.assertIn("ventes", tables)
                self.assertIn("lignes_vente", tables)
        finally:
            # Nettoyer
            os.close(db_fd)
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
