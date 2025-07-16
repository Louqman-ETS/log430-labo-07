#!/bin/bash

# Script de test d'intégration pour les scénarios de saga
# Ce script teste les vraies APIs sans mocks

KONG_URL="http://localhost:8000"
API_KEY="admin-api-key-12345"

echo "Tests d'intégration des scénarios de saga"
echo "============================================"
echo ""

# Fonction pour faire une requête avec gestion d'erreur
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo "REQUEST: $description"
    echo "   $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
            -X "$method" \
            -H "Content-Type: application/json" \
            -H "apikey: $API_KEY" \
            -d "$data" \
            "$url")
    else
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
            -X "$method" \
            -H "apikey: $API_KEY" \
            "$url")
    fi
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')
    
    echo "   Status: $http_code"
    echo "   Response: $body" | jq '.' 2>/dev/null || echo "   Response: $body"
    echo ""
    
    return $http_code
}

echo "Test 1: Saga COMPLÉTÉE avec client existant"
echo "----------------------------------------------"

# Données pour une saga qui devrait réussir
success_data='{
    "cart_id": 123,
    "products": [
        {"product_id": 1, "quantity": 1, "price": 29.99}
    ],
    "shipping_address": "123 Test Street, Test City",
    "billing_address": "123 Test Street, Test City", 
    "payment_method": "credit_card",
    "simulate_failure": false
}'

make_request "POST" "$KONG_URL/api/v1/customers/1/order-processing" "$success_data" "Démarrage saga pour client ID 1"

if [ $? -eq 202 ]; then
    echo "SUCCÈS: Saga démarrée avec succès!"
    
    # Extraire l'ID de la saga
    saga_id=$(echo "$body" | jq -r '.saga_id' 2>/dev/null)
    
    if [ "$saga_id" != "null" ] && [ -n "$saga_id" ]; then
        echo "   Saga ID: $saga_id"
        
        # Attendre que la saga se termine
        echo "ATTENTE: 3 secondes pour que la saga se termine..."
        sleep 3
        
        # Vérifier le statut final
        make_request "GET" "$KONG_URL/api/v1/sagas/$saga_id" "" "Vérification du statut final de la saga"
        
        # Vérifier les événements
        make_request "GET" "$KONG_URL/api/v1/sagas/$saga_id/events" "" "Récupération des événements de la saga"
    fi
else
    echo "ERREUR: Échec du démarrage de la saga"
fi

echo ""
echo "Test 2: Saga COMPENSÉE avec client inexistant"
echo "-----------------------------------------------"

# Test avec un client qui n'existe pas
compensation_data='{
    "cart_id": 456,
    "products": [
        {"product_id": 2, "quantity": 2, "price": 49.99}
    ],
    "shipping_address": "456 Fail Street, Fail City",
    "billing_address": "456 Fail Street, Fail City",
    "payment_method": "credit_card",
    "simulate_failure": false
}'

make_request "POST" "$KONG_URL/api/v1/customers/99999/order-processing" "$compensation_data" "Démarrage saga pour client inexistant (ID 99999)"

if [ $? -eq 400 ]; then
    echo "SUCCÈS: Échec attendu pour client inexistant!"
elif [ $? -eq 202 ]; then
    echo "COMPENSATION: Saga démarrée - devrait se compenser..."
    
    # Extraire l'ID de la saga
    saga_id=$(echo "$body" | jq -r '.saga_id' 2>/dev/null)
    
    if [ "$saga_id" != "null" ] && [ -n "$saga_id" ]; then
        echo "   Saga ID: $saga_id"
        
        # Attendre que la saga se compense
        echo "ATTENTE: 5 secondes pour que la saga se compense..."
        sleep 5
        
        # Vérifier le statut final
        make_request "GET" "$KONG_URL/api/v1/sagas/$saga_id" "" "Vérification du statut final de la saga compensée"
        
        # Vérifier les événements de compensation
        make_request "GET" "$KONG_URL/api/v1/sagas/$saga_id/events" "" "Récupération des événements de compensation"
    fi
else
    echo "ERREUR: Réponse inattendue"
fi

echo ""
echo "Test 3: Saga avec simulation d'échec"
echo "--------------------------------------"

# Test avec le flag simulate_failure
failure_simulation_data='{
    "cart_id": 789,
    "products": [
        {"product_id": 1, "quantity": 1, "price": 19.99}
    ],
    "shipping_address": "789 Simulate Street, Fail City",
    "billing_address": "789 Simulate Street, Fail City",
    "payment_method": "credit_card",
    "simulate_failure": true
}'

make_request "POST" "$KONG_URL/api/v1/customers/2/order-processing" "$failure_simulation_data" "Démarrage saga avec simulation d'échec"

if [ $? -eq 202 ]; then
    echo "SIMULATION: Saga démarrée avec simulation d'échec..."
    
    # Extraire l'ID de la saga
    saga_id=$(echo "$body" | jq -r '.saga_id' 2>/dev/null)
    
    if [ "$saga_id" != "null" ] && [ -n "$saga_id" ]; then
        echo "   Saga ID: $saga_id"
        
        # Attendre que la saga échoue et se compense
        echo "ATTENTE: 4 secondes pour que la saga échoue et se compense..."
        sleep 4
        
        # Vérifier le statut final
        make_request "GET" "$KONG_URL/api/v1/sagas/$saga_id" "" "Vérification du statut final de la saga avec échec simulé"
    fi
else
    echo "ERREUR: Échec du démarrage de la saga avec simulation d'échec"
fi

echo ""
echo "Test 4: Vérification des métriques et statistiques"
echo "----------------------------------------------------"

make_request "GET" "$KONG_URL/api/v1/sagas/stats/summary" "" "Récupération des statistiques des sagas"

make_request "GET" "$KONG_URL/metrics" "" "Récupération des métriques Prometheus"

echo ""
echo "Tests d'intégration terminés!"
echo ""
echo "CONSEILS:"
echo "   - Consultez le dashboard Grafana pour voir les métriques en temps réel"
echo "   - Les logs détaillés sont disponibles dans les conteneurs saga-orchestrator"
echo "   - Utilisez 'docker logs saga-orchestrator-1' pour voir les logs" 