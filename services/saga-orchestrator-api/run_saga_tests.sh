#!/bin/bash

# Script pour lancer les tests des scénarios de saga

echo "Lancement des tests pour les scénarios de saga..."
echo "=================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "src/main.py" ]; then
    echo "ERREUR: Ce script doit être lancé depuis le répertoire saga-orchestrator-api"
    exit 1
fi

# Installer les dépendances de test si nécessaire
echo "Installation des dépendances de test..."
pip install -r requirements.txt

# Lancer les tests avec pytest
echo ""
echo "Exécution des tests de scénarios de saga..."
echo ""

# Test du scénario saga complétée
echo "Test du scénario de saga COMPLÉTÉE:"
pytest tests/test_saga_scenarios.py::TestSagaCompletedScenario -v

echo ""
echo "Test du scénario de saga COMPENSÉE:"
pytest tests/test_saga_scenarios.py::TestSagaCompensatedScenario -v

echo ""
echo "Test des cas limites:"
pytest tests/test_saga_scenarios.py::TestSagaEdgeCases -v

echo ""
echo "Test de couverture complète des scénarios:"
pytest tests/test_saga_scenarios.py -v --tb=short

echo ""
echo "Tests terminés!"
echo "Consultez les résultats ci-dessus pour vérifier le comportement des sagas." 