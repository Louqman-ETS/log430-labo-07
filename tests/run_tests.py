#!/usr/bin/env python

import unittest
import sys
import os


def run_tests():
    """Découvre et exécute tous les nouveaux tests dans le dossier tests"""
    print("🧪 LANCEMENT DES TESTS - APPLICATION FLASK MULTI-MAGASINS")
    print("=" * 60)

    # Configurer le chemin pour les tests
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)

    # Ajouter le répertoire du projet au path pour que les imports fonctionnent
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Tests spécifiques à exécuter dans l'ordre
    test_modules = [
        "tests.test_app",  # Tests principaux de structure
        "tests.test_functionality",  # Tests fonctionnels
    ]

    total_tests = 0
    total_failures = 0
    total_errors = 0

    for test_module in test_modules:
        print(f"\n📋 Module: {test_module}")
        print("-" * 40)

        try:
            # Charger le module de test
            suite = unittest.TestLoader().loadTestsFromName(test_module)

            # Exécuter les tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            # Accumuler les statistiques
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)

        except Exception as e:
            print(f"❌ Erreur lors du chargement du module {test_module}: {e}")
            total_errors += 1

    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Tests exécutés: {total_tests}")
    print(f"❌ Échecs: {total_failures}")
    print(f"💥 Erreurs: {total_errors}")

    if total_failures == 0 and total_errors == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✨ Application prête pour utilisation")
    else:
        print(f"\n⚠️  {total_failures + total_errors} problème(s) détecté(s)")
        print("🔧 Vérifiez les erreurs ci-dessus")

    print("=" * 60)

    # Retourner un code d'erreur approprié
    return 0 if (total_failures == 0 and total_errors == 0) else 1


if __name__ == "__main__":
    sys.exit(run_tests())
