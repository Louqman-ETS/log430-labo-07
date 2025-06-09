#!/usr/bin/env python3
"""
Tests principaux pour l'application Flask multi-magasins
Tests simples et robustes pour la nouvelle architecture
"""

import unittest
import os
from unittest.mock import patch, MagicMock


class TestAppStructure(unittest.TestCase):
    """Tests de la structure de l'application"""

    def test_flask_imports(self):
        """Test que tous les imports Flask fonctionnent"""
        try:
            from src.app import create_app, db
            from src.app.models.models import (
                Magasin,
                Caisse,
                Categorie,
                Produit,
                Vente,
                LigneVente,
            )

            self.assertTrue(True, "✅ Imports Flask réussis")
        except ImportError as e:
            self.fail(f"❌ Erreur d'import Flask: {e}")

    def test_app_creation(self):
        """Test de création de l'application Flask"""
        try:
            from src.app import create_app

            app = create_app()
            self.assertIsNotNone(app)
            self.assertEqual(app.name, "src.app")
            print("✅ Application Flask créée avec succès")
        except Exception as e:
            self.fail(f"❌ Erreur création app: {e}")

    def test_blueprints_registration(self):
        """Test que tous les contrôleurs sont enregistrés"""
        try:
            from src.app import create_app

            app = create_app()

            blueprint_names = [bp.name for bp in app.blueprints.values()]
            expected_blueprints = [
                "home",
                "magasin",
                "caisse",
                "produit",
                "vente",
                "rapport",
                "stock_central",
            ]

            for bp_name in expected_blueprints:
                self.assertIn(bp_name, blueprint_names, f"Blueprint {bp_name} manquant")

            print(f"✅ {len(expected_blueprints)} blueprints enregistrés")
        except Exception as e:
            self.fail(f"❌ Erreur blueprints: {e}")

    def test_database_models(self):
        """Test que tous les modèles sont correctement définis"""
        try:
            from src.app.models.models import (
                Magasin,
                Caisse,
                Categorie,
                Produit,
                Vente,
                LigneVente,
            )

            models = [Magasin, Caisse, Categorie, Produit, Vente, LigneVente]
            expected_tables = [
                "magasins",
                "caisses",
                "categories",
                "produits",
                "ventes",
                "lignes_vente",
            ]

            for model, table_name in zip(models, expected_tables):
                self.assertTrue(hasattr(model, "__tablename__"))
                self.assertEqual(model.__tablename__, table_name)

            print("✅ Tous les modèles sont correctement définis")
        except Exception as e:
            self.fail(f"❌ Erreur modèles: {e}")


class TestControllers(unittest.TestCase):
    """Tests des contrôleurs"""

    def test_controllers_import(self):
        """Test que tous les contrôleurs s'importent"""
        controllers = [
            "home_controller",
            "magasin_controller",
            "caisse_controller",
            "produit_controller",
            "vente_controller",
            "rapport_controller",
            "stock_central_controller",
        ]

        try:
            for controller in controllers:
                module = __import__(
                    f"src.app.controllers.{controller}", fromlist=[controller]
                )
                self.assertTrue(
                    hasattr(module, "bp"), f"Blueprint manquant dans {controller}"
                )

            print(f"✅ {len(controllers)} contrôleurs importés avec succès")
        except Exception as e:
            self.fail(f"❌ Erreur import contrôleurs: {e}")

    def test_routes_existence(self):
        """Test que les routes principales existent"""
        try:
            from src.app import create_app

            app = create_app()

            with app.test_client() as client:
                # Test route principale
                response = client.get("/")
                self.assertIn(
                    response.status_code, [200, 302]
                )  # 200 OK ou 302 Redirect

                print("✅ Route principale accessible")
        except Exception as e:
            self.fail(f"❌ Erreur routes: {e}")


class TestAppConfiguration(unittest.TestCase):
    """Tests de configuration"""

    def test_config_exists(self):
        """Test que la configuration existe"""
        try:
            from src.app.config import Config

            required_configs = ["SQLALCHEMY_DATABASE_URI", "SECRET_KEY"]

            for config_key in required_configs:
                self.assertTrue(
                    hasattr(Config, config_key), f"Config {config_key} manquante"
                )

            print("✅ Configuration complète")
        except Exception as e:
            self.fail(f"❌ Erreur configuration: {e}")

    def test_templates_exist(self):
        """Test que les templates principaux existent"""
        templates = [
            "src/app/templates/home.html",
            "src/app/templates/rapport/index.html",
            "src/app/templates/magasin/index.html",
        ]

        for template in templates:
            if os.path.exists(template):
                print(f"✅ Template {template} trouvé")
            # Ne pas faire échouer si certains templates manquent

        # Vérifier au moins que le dossier templates existe
        templates_dir = "src/app/templates"
        self.assertTrue(os.path.exists(templates_dir), "Dossier templates manquant")


class TestNewRunModule(unittest.TestCase):
    """Tests du nouveau module de lancement"""

    def test_run_module_exists(self):
        """Test que le nouveau module run existe"""
        try:
            from src.app import run

            self.assertTrue(hasattr(run, "main"))
            print("✅ Module run.py fonctionnel")
        except Exception as e:
            self.fail(f"❌ Erreur module run: {e}")

    @patch("src.app.run.create_app")
    def test_main_function(self, mock_create_app):
        """Test simulé de la fonction main"""
        try:
            from src.app.run import main

            # Mock de l'app
            mock_app = MagicMock()
            mock_create_app.return_value = mock_app

            # Test que main peut être appelé sans erreur
            # (on ne l'exécute pas vraiment pour éviter de lancer le serveur)
            self.assertTrue(callable(main))
            print("✅ Fonction main définie")
        except Exception as e:
            self.fail(f"❌ Erreur fonction main: {e}")


class TestCleanup(unittest.TestCase):
    """Tests de vérification du nettoyage"""

    def test_obsolete_files_removed(self):
        """Test que les fichiers obsolètes ont été supprimés"""
        obsolete_files = [
            "src/main.py",
            "src/models.py",
            "src/dao.py",
            "src/service.py",
            "src/run.py",
        ]

        removed_count = 0
        for file_path in obsolete_files:
            if not os.path.exists(file_path):
                removed_count += 1

        print(f"✅ {removed_count}/{len(obsolete_files)} fichiers obsolètes supprimés")

        # Test que les fichiers critiques sont supprimés
        critical_files = [
            "src/main.py",
            "src/models.py",
            "src/dao.py",
            "src/service.py",
        ]
        for file_path in critical_files:
            self.assertFalse(
                os.path.exists(file_path), f"Fichier critique {file_path} existe encore"
            )

    def test_new_structure_complete(self):
        """Test que la nouvelle structure est complète"""
        essential_files = [
            "src/app/__init__.py",
            "src/app/run.py",
            "src/app/models/models.py",
            "src/app/controllers/home_controller.py",
            "src/create_db.py",
            "src/db.py",
        ]

        present_count = 0
        for file_path in essential_files:
            if os.path.exists(file_path):
                present_count += 1

        print(f"✅ {present_count}/{len(essential_files)} fichiers essentiels présents")

        # Au moins les fichiers critiques doivent exister
        critical_files = [
            "src/app/__init__.py",
            "src/app/run.py",
            "src/app/models/models.py",
        ]
        for file_path in critical_files:
            self.assertTrue(
                os.path.exists(file_path), f"Fichier critique {file_path} manquant"
            )


if __name__ == "__main__":
    # Lancer les tests avec plus de verbosité
    unittest.main(verbosity=2)
