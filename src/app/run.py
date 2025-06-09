#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Flask
Usage: python -m src.app.run
"""

import os
import sys

# Ajouter le répertoire racine au path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app import create_app, db
from src.app.models.models import Caisse, Categorie, Magasin


def main():
    """Fonction principale pour lancer l'application"""

    print("🚀 Démarrage de l'application Multi-Magasins...")

    # Créer l'application Flask
    app = create_app()

    # Créer les tables de la base de données si elles n'existent pas
    with app.app_context():
        print("🔄 Vérification de la base de données...")
        try:
            # Forcer le rechargement des métadonnées de la base de données
            db.engine.dispose()  # Fermer toutes les connexions
            db.reflect()  # Recharger les métadonnées

            db.create_all()
            print("✅ Base de données prête")

            # Vérifier qu'on a des données
            nb_magasins = Magasin.query.count()
            nb_caisses = Caisse.query.count()
            nb_categories = Categorie.query.count()

            print(f"📊 Données actuelles:")
            print(f"   • {nb_magasins} magasins")
            print(f"   • {nb_caisses} caisses")
            print(f"   • {nb_categories} catégories")

            if nb_magasins == 0:
                print("⚠️  Aucun magasin trouvé. L'application va démarrer quand même.")
                print("   Vous pouvez exécuter: python -m src.create_db")

        except Exception as e:
            print(f"❌ Erreur base de données: {e}")
            print("\n💡 Solution:")
            print("   1. Vérifiez que PostgreSQL fonctionne")
            print("   2. Exécutez: python -m src.create_db")
            return

    # Lancer l'application
    print("\n🌐 Lancement du serveur web...")
    print("📱 Application disponible sur: http://127.0.0.1:8080")
    print("🛑 Arrêter avec Ctrl+C")
    print("-" * 50)

    try:
        # Utiliser les variables d'environnement ou des valeurs par défaut
        host = os.getenv("HOST", "0.0.0.0")  # 0.0.0.0 pour Docker
        port = int(os.getenv("PORT", 8080))
        debug = os.getenv("FLASK_DEBUG", "1") == "1"

        app.run(debug=debug, host=host, port=port)
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")


if __name__ == "__main__":
    main()
