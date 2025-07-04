#!/bin/bash

# Script de configuration Kong pour les microservices DDD
# Ce script configure le routage dynamique, les clés API et le logging centralisé

set -e

KONG_ADMIN_URL="http://localhost:9001"

echo "🚀 Configuration de Kong API Gateway pour les microservices DDD"
echo "=================================================="

# Fonction pour attendre que Kong soit prêt
wait_for_kong() {
    echo "⏳ Attente de Kong..."
    while ! curl -s "$KONG_ADMIN_URL" > /dev/null; do
        echo "   Kong n'est pas encore prêt, attente..."
        sleep 5
    done
    echo "✅ Kong est prêt!"
}

# Fonction pour créer un service
create_service() {
    local name=$1
    local url=$2
    local path_prefix=$3
    
    echo "📡 Création du service: $name"
    curl -s -X POST "$KONG_ADMIN_URL/services" \
        --data "name=$name" \
        --data "url=$url" \
        --data "protocol=http" \
        --data "connect_timeout=60000" \
        --data "write_timeout=60000" \
        --data "read_timeout=60000" > /dev/null
    
    echo "🛣️  Création de la route pour: $name"
    curl -s -X POST "$KONG_ADMIN_URL/services/$name/routes" \
        --data "name=${name}-route" \
        --data "paths[]=$path_prefix" \
        --data "strip_path=true" \
        --data "preserve_host=false" > /dev/null
    
    echo "✅ Service $name configuré"
}

# Fonction pour activer un plugin sur un service
enable_plugin() {
    local service_name=$1
    local plugin_name=$2
    local config=$3
    
    echo "🔌 Activation du plugin $plugin_name sur $service_name"
    if [ -n "$config" ]; then
        curl -s -X POST "$KONG_ADMIN_URL/services/$service_name/plugins" \
            --data "name=$plugin_name" \
            --data "$config" > /dev/null
    else
        curl -s -X POST "$KONG_ADMIN_URL/services/$service_name/plugins" \
            --data "name=$plugin_name" > /dev/null
    fi
}

# Fonction pour créer un consommateur
create_consumer() {
    local username=$1
    local custom_id=$2
    
    echo "👤 Création du consommateur: $username"
    curl -s -X POST "$KONG_ADMIN_URL/consumers" \
        --data "username=$username" \
        --data "custom_id=$custom_id" > /dev/null
}

# Fonction pour créer une clé API
create_api_key() {
    local consumer=$1
    local key=$2
    
    echo "🔑 Création de la clé API pour: $consumer"
    if [ -n "$key" ]; then
        curl -s -X POST "$KONG_ADMIN_URL/consumers/$consumer/key-auth" \
            --data "key=$key" > /dev/null
    else
        curl -s -X POST "$KONG_ADMIN_URL/consumers/$consumer/key-auth" > /dev/null
    fi
}

# Attendre que Kong soit prêt
wait_for_kong

echo ""
echo "🏗️  CONFIGURATION DES SERVICES"
echo "================================"

# Créer les services pour nos microservices
create_service "inventory-api" "http://inventory-api:8001" "/inventory"
create_service "retail-api" "http://retail-api:8002" "/retail"
create_service "ecommerce-api" "http://ecommerce-api:8000" "/ecommerce"
create_service "reporting-api" "http://reporting-api:8005" "/reporting"

echo ""
echo "🔐 CONFIGURATION DE L'AUTHENTIFICATION"
echo "======================================"

# Activer l'authentification par clé API sur tous les services
enable_plugin "inventory-api" "key-auth" ""
enable_plugin "retail-api" "key-auth" ""
enable_plugin "ecommerce-api" "key-auth" ""
enable_plugin "reporting-api" "key-auth" ""

echo ""
echo "👥 CRÉATION DES CONSOMMATEURS ET CLÉS API"
echo "=========================================="

# Créer des consommateurs et leurs clés API
create_consumer "admin-user" "admin-001"
create_api_key "admin-user" "admin-api-key-12345"

create_consumer "frontend-app" "frontend-001"
create_api_key "frontend-app" "frontend-api-key-67890"

create_consumer "mobile-app" "mobile-001"
create_api_key "mobile-app" "mobile-api-key-abcde"

create_consumer "external-partner" "partner-001"
create_api_key "external-partner" "partner-api-key-fghij"

echo ""
echo "📊 CONFIGURATION DU LOGGING ET MONITORING"
echo "=========================================="

# Activer le logging centralisé avec file-log
enable_plugin "inventory-api" "file-log" "config.path=/var/log/kong/inventory-api.log"
enable_plugin "retail-api" "file-log" "config.path=/var/log/kong/retail-api.log"
enable_plugin "ecommerce-api" "file-log" "config.path=/var/log/kong/ecommerce-api.log"
enable_plugin "reporting-api" "file-log" "config.path=/var/log/kong/reporting-api.log"

# Activer la limitation de taux (rate limiting)
enable_plugin "inventory-api" "rate-limiting" "config.minute=100&config.hour=1000"
enable_plugin "retail-api" "rate-limiting" "config.minute=100&config.hour=1000"
enable_plugin "ecommerce-api" "rate-limiting" "config.minute=200&config.hour=2000"
enable_plugin "reporting-api" "rate-limiting" "config.minute=50&config.hour=500"

# Activer la transformation des requêtes pour ajouter des headers de traçabilité
enable_plugin "inventory-api" "request-transformer" "config.add.headers=X-Service-Name:inventory-api,X-Gateway:kong"
enable_plugin "retail-api" "request-transformer" "config.add.headers=X-Service-Name:retail-api,X-Gateway:kong"
enable_plugin "ecommerce-api" "request-transformer" "config.add.headers=X-Service-Name:ecommerce-api,X-Gateway:kong"
enable_plugin "reporting-api" "request-transformer" "config.add.headers=X-Service-Name:reporting-api,X-Gateway:kong"

echo ""
echo "✅ CONFIGURATION TERMINÉE!"
echo "========================="
echo ""
echo "🌐 Endpoints Kong:"
echo "   - Proxy: http://localhost:9000"
echo "   - Admin API: http://localhost:9001"
echo "   - Manager GUI: http://localhost:9002"
echo "   - Konga GUI: http://localhost:1337"
echo ""
echo "🛣️  Routes des services:"
echo "   - Inventory API: http://localhost:9000/inventory/api/v1/"
echo "   - Retail API: http://localhost:9000/retail/api/v1/"
echo "   - Ecommerce API: http://localhost:9000/ecommerce/api/v1/"
echo "   - Reporting API: http://localhost:9000/reporting/api/v1/"
echo ""
echo "🔑 Clés API créées:"
echo "   - Admin: admin-api-key-12345"
echo "   - Frontend: frontend-api-key-67890"
echo "   - Mobile: mobile-api-key-abcde"
echo "   - Partner: partner-api-key-fghij"
echo ""
echo "📋 Utilisation:"
echo "   curl -H 'apikey: admin-api-key-12345' http://localhost:9000/inventory/api/v1/products/"
echo "" 