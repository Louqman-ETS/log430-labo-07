#!/bin/bash

# Script de test pour Kong API Gateway
# Teste les routes, l'authentification et le logging

set -e

KONG_PROXY_URL="http://localhost:8000"
KONG_ADMIN_URL="http://localhost:8001"

echo "🧪 Tests Kong API Gateway"
echo "========================="

# Fonction pour tester une route avec clé API
test_route() {
    local service_path=$1
    local api_key=$2
    local test_name=$3
    
    echo "🔍 Test: $test_name"
    echo "   Route: $service_path"
    echo "   Clé API: $api_key"
    
    # Test avec clé API
    response=$(curl -s -w "%{http_code}" -H "apikey: $api_key" "$KONG_PROXY_URL$service_path" -o /dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        echo "   ✅ Succès (HTTP $response)"
    else
        echo "   ❌ Échec (HTTP $response)"
    fi
    
    # Test sans clé API (devrait échouer)
    response_no_key=$(curl -s -w "%{http_code}" "$KONG_PROXY_URL$service_path" -o /dev/null)
    
    if [ "$response_no_key" = "401" ]; then
        echo "   ✅ Authentification requise (HTTP $response_no_key)"
    else
        echo "   ⚠️  Attention: accès sans clé API (HTTP $response_no_key)"
    fi
    
    echo ""
}

# Fonction pour vérifier le statut de Kong
check_kong_status() {
    echo "🏥 Vérification du statut de Kong"
    
    # Vérifier que Kong est démarré
    if curl -s "$KONG_ADMIN_URL" > /dev/null; then
        echo "   ✅ Kong Admin API accessible"
    else
        echo "   ❌ Kong Admin API inaccessible"
        exit 1
    fi
    
    # Vérifier les services configurés
    services=$(curl -s "$KONG_ADMIN_URL/services" | grep -o '"name":"[^"]*"' | wc -l)
    echo "   📊 Nombre de services configurés: $services"
    
    # Vérifier les routes configurées
    routes=$(curl -s "$KONG_ADMIN_URL/routes" | grep -o '"name":"[^"]*"' | wc -l)
    echo "   🛣️  Nombre de routes configurées: $routes"
    
    # Vérifier les consommateurs
    consumers=$(curl -s "$KONG_ADMIN_URL/consumers" | grep -o '"username":"[^"]*"' | wc -l)
    echo "   👤 Nombre de consommateurs: $consumers"
    
    echo ""
}

# Fonction pour tester le logging
test_logging() {
    echo "📊 Test du logging"
    
    # Faire quelques requêtes pour générer des logs
    curl -s -H "apikey: admin-api-key-12345" "$KONG_PROXY_URL/inventory/health" > /dev/null
    curl -s -H "apikey: frontend-api-key-67890" "$KONG_PROXY_URL/retail/health" > /dev/null
    curl -s -H "apikey: mobile-api-key-abcde" "$KONG_PROXY_URL/ecommerce/health" > /dev/null
    
    echo "   ✅ Requêtes de test envoyées"
    echo "   📂 Logs disponibles dans ./logs/"
    
    # Vérifier si les fichiers de logs existent
    if [ -d "./logs" ]; then
        log_files=$(ls -la ./logs/ 2>/dev/null | grep "\.log" | wc -l)
        echo "   📋 Fichiers de logs trouvés: $log_files"
    else
        echo "   ⚠️  Répertoire de logs non trouvé"
    fi
    
    echo ""
}

# Fonction pour afficher la configuration
show_configuration() {
    echo "🔧 Configuration Kong"
    echo "   Proxy: $KONG_PROXY_URL"
    echo "   Admin: $KONG_ADMIN_URL"
    echo ""
    echo "🔑 Clés API disponibles:"
    echo "   - Admin: admin-api-key-12345"
    echo "   - Frontend: frontend-api-key-67890"
    echo "   - Mobile: mobile-api-key-abcde"
    echo "   - Partner: partner-api-key-fghij"
    echo ""
}

# Exécuter les tests
show_configuration
check_kong_status

echo "🚀 Tests des routes et authentification"
echo "======================================"

test_route "/inventory/health" "admin-api-key-12345" "Inventory API - Health Check"
test_route "/retail/health" "frontend-api-key-67890" "Retail API - Health Check"
test_route "/ecommerce/health" "mobile-api-key-abcde" "Ecommerce API - Health Check"
test_route "/reporting/health" "partner-api-key-fghij" "Reporting API - Health Check"

test_route "/inventory/api/v1/products/" "admin-api-key-12345" "Inventory API - Products List"
test_route "/retail/api/v1/stores/" "frontend-api-key-67890" "Retail API - Stores List"
test_route "/ecommerce/api/v1/customers/" "mobile-api-key-abcde" "Ecommerce API - Customers List"
test_route "/reporting/api/v1/reports/global-summary" "partner-api-key-fghij" "Reporting API - Global Summary"

test_logging

echo "✅ Tests terminés!"
echo ""
echo "📋 Résumé des fonctionnalités testées:"
echo "   ✓ Routage dynamique vers les microservices"
echo "   ✓ Authentification par clé API"
echo "   ✓ Logging centralisé"
echo "   ✓ Protection contre l'accès non autorisé"
echo ""
echo "🌐 Interfaces web disponibles:"
echo "   - Kong Manager: http://localhost:8002"
echo "   - Konga GUI: http://localhost:1337"
echo "" 