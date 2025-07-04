#!/bin/bash

echo "🔧 Application de la configuration Kong déclarative avec CORS"
echo "============================================================"

# Vérifier si Kong est démarré
if ! curl -s http://localhost:9001 > /dev/null; then
    echo "❌ Kong n'est pas démarré."
    echo "💡 Démarrez Kong d'abord avec: make -f Makefile.kong kong-up"
    exit 1
fi

# Attendre que Kong soit prêt
echo "⏳ Vérification que Kong est prêt..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:9001/status > /dev/null; then
        echo "✅ Kong est prêt!"
        break
    fi
    echo "   Tentative $attempt/$max_attempts..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Kong n'est pas accessible après 60 secondes"
    exit 1
fi

# Appliquer la configuration déclarative
echo ""
echo "📋 Application de la configuration déclarative..."
echo "   Fichier: kong/kong-declarative.yml"

response=$(curl -s -X POST http://localhost:9001/config \
  -F config=@kong/kong-declarative.yml)

if echo "$response" | grep -q "error"; then
    echo "❌ Erreur lors de l'application de la configuration:"
    echo "$response"
    exit 1
else
    echo "✅ Configuration appliquée avec succès!"
fi

# Vérifier les services
echo ""
echo "🔍 Vérification des services configurés..."
services=$(curl -s http://localhost:9001/services | jq -r '.data[] | .name' 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "Services configurés:"
    echo "$services" | sed 's/^/  - /'
else
    echo "Services configurés:"
    curl -s http://localhost:9001/services | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g' | sed 's/^/  - /'
fi

# Vérifier les plugins CORS
echo ""
echo "🔍 Vérification des plugins CORS..."
cors_count=$(curl -s http://localhost:9001/plugins | grep -c '"name":"cors"' 2>/dev/null || echo "0")
echo "Plugins CORS configurés: $cors_count"

# Vérifier les consommateurs
echo ""
echo "🔍 Vérification des consommateurs..."
consumers=$(curl -s http://localhost:9001/consumers | jq -r '.data[] | .username' 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "Consommateurs configurés:"
    echo "$consumers" | sed 's/^/  - /'
else
    echo "Consommateurs configurés:"
    curl -s http://localhost:9001/consumers | grep -o '"username":"[^"]*"' | sed 's/"username":"//g' | sed 's/"//g' | sed 's/^/  - /'
fi

echo ""
echo "🎉 Configuration Kong avec CORS terminée!"
echo "========================================"
echo ""
echo "🌐 Endpoints Kong:"
echo "  - Proxy: http://localhost:9000"
echo "  - Admin API: http://localhost:9001"
echo ""
echo "🛣️  Routes avec CORS configuré:"
echo "  - Inventory: http://localhost:9000/inventory/"
echo "  - Ecommerce: http://localhost:9000/ecommerce/"
echo "  - Retail: http://localhost:9000/retail/"
echo "  - Reporting: http://localhost:9000/reporting/"
echo ""
echo "🔑 Clés API disponibles:"
echo "  - Admin: admin-api-key-12345"
echo "  - Frontend: frontend-api-key-67890"
echo "  - Mobile: mobile-api-key-abcde"
echo "  - Partner: partner-api-key-fghij"
echo ""
echo "🧪 Test CORS rapide:"
echo "curl -X OPTIONS http://localhost:9000/inventory/ \\"
echo "  -H 'Origin: http://localhost:3000' \\"
echo "  -H 'Access-Control-Request-Method: GET' -v" 