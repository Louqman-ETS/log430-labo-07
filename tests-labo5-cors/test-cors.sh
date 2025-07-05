#!/bin/bash

echo "🧪 Test CORS Configuration"
echo "=========================="

# Configuration
KONG_URL="http://localhost:9000"
API_KEY="admin-api-key-12345"

# Test 1: Requête preflight OPTIONS
echo ""
echo "🔍 Test 1: Requête preflight OPTIONS"
echo "-----------------------------------"
echo "curl -X OPTIONS $KONG_URL/inventory/ -H 'Origin: http://localhost:3000' -H 'Access-Control-Request-Method: GET'"
echo ""

response=$(curl -s -X OPTIONS "$KONG_URL/inventory/" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: apikey,content-type" \
  -I)

echo "$response"

if echo "$response" | grep -q "Access-Control-Allow-Origin: http://localhost:3000"; then
    echo "✅ CORS preflight: OK"
else
    echo "❌ CORS preflight: ÉCHEC"
fi

# Test 2: Requête GET avec origin autorisé
echo ""
echo "🔍 Test 2: Requête GET avec origin autorisé"
echo "------------------------------------------"
echo "curl -H 'Origin: http://localhost:3000' -H 'apikey: $API_KEY' $KONG_URL/inventory/api/v1/products/"
echo ""

response=$(curl -s -X GET "$KONG_URL/inventory/api/v1/products/" \
  -H "Origin: http://localhost:3000" \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -I)

echo "$response" | head -10

if echo "$response" | grep -q "Access-Control-Allow-Origin: http://localhost:3000"; then
    echo "✅ CORS GET request: OK"
else
    echo "❌ CORS GET request: ÉCHEC"
fi

# Test 3: Vérification des headers CORS
echo ""
echo "🔍 Test 3: Vérification des headers CORS"
echo "---------------------------------------"

cors_headers=$(echo "$response" | grep -i "access-control")
if [ -n "$cors_headers" ]; then
    echo "Headers CORS trouvés:"
    echo "$cors_headers"
    echo "✅ Headers CORS: OK"
else
    echo "❌ Aucun header CORS trouvé"
fi

# Test 4: Test avec origin non autorisé
echo ""
echo "🔍 Test 4: Origin non autorisé"
echo "-----------------------------"

response_unauthorized=$(curl -s -X GET "$KONG_URL/inventory/" \
  -H "Origin: http://malicious-site.com" \
  -H "apikey: $API_KEY" \
  -I)

if echo "$response_unauthorized" | grep -q "Access-Control-Allow-Origin: http://malicious-site.com"; then
    echo "❌ Sécurité CORS: ÉCHEC (origin non autorisé accepté)"
else
    echo "✅ Sécurité CORS: OK (origin non autorisé rejeté)"
fi

echo ""
echo "🎉 Tests CORS terminés!"
echo "======================" 