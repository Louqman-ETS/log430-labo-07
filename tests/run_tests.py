#!/usr/bin/env python

import unittest
import sys
import os

def run_tests():
    """Découvre et exécute tous les tests dans le dossier tests"""
    # Configurer le chemin pour les tests
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    # Ajouter le répertoire du projet au path pour que les imports fonctionnent
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    # Découvrir et exécuter les tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retourner un code d'erreur approprié
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 