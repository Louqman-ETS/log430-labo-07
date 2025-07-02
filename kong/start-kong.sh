#!/bin/bash

echo "🚀 Démarrage Kong API Gateway"
echo "=============================="

# Vérifier que le réseau microservices existe
echo "🔍 Vérification du réseau microservices..."
if ! docker network ls | grep -q "microservices-network"; then
    echo "❌ Le réseau microservices-network n'existe pas!"
    echo "💡 Démarrez d'abord vos microservices avec:"
    echo "   cd services && docker-compose up -d"
    exit 1
fi

# Vérifier la configuration Kong
echo "🔧 Vérification de la configuration Kong..."
if [ ! -f "kong/kong.yml" ]; then
    echo "❌ Fichier de configuration kong.yml introuvable!"
    exit 1
fi

# Créer le répertoire de logs si nécessaire
mkdir -p kong/logging/logs

# Démarrer Kong
echo "🚀 Démarrage de Kong Gateway..."
docker-compose -f docker-compose.kong.yml up -d

# Attendre que Kong soit prêt
echo "⏳ Attente du démarrage de Kong..."
for i in {1..30}; do
    if curl -s http://localhost:8001 > /dev/null; then
        echo "✅ Kong est prêt!"
        break
    fi
    echo "   Tentative $i/30..."
    sleep 2
done

# Vérifier l'état
echo ""
echo "📊 État des services Kong:"
docker-compose -f docker-compose.kong.yml ps

echo ""
echo "🎯 Points d'accès Kong:"
echo "   • Gateway Proxy: http://localhost:8000"
echo "   • Admin API: http://localhost:8001"
echo "   • Logging Service: http://localhost:3000"
echo ""
echo "🔑 Test avec clé API (exemple):"
echo "   curl -H 'X-API-Key: frontend-web-app-key-2024' http://localhost:8000/api/v1/products" 