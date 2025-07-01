#!/bin/bash

# Script de test pour valider l'architecture des microservices
set -e

echo "🧪 Testing Microservices Architecture"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    
    if response=$(curl -s "$url" 2>/dev/null); then
        if echo "$response" | grep -q "$expected"; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        else
            echo -e "${RED}❌ FAIL - Unexpected response${NC}"
            echo "Response: $response"
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL - No response${NC}"
        return 1
    fi
}

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

echo ""
echo "1. Testing individual service health..."
echo "-------------------------------------"

test_endpoint "Products API Health" "http://localhost:8001/health" "products"
test_endpoint "Stores API Health" "http://localhost:8002/health" "stores" 
test_endpoint "Reporting API Health" "http://localhost:8003/health" "reporting"

echo ""
echo "2. Testing data endpoints..."
echo "--------------------------"

test_endpoint "Products List" "http://localhost:8001/api/v1/products/" "items"
test_endpoint "Categories List" "http://localhost:8001/api/v1/categories/" "Alimentaire"
test_endpoint "Stores List" "http://localhost:8002/api/v1/stores/" "items"
test_endpoint "Cash Registers" "http://localhost:8002/api/v1/cash-registers/" "Caisse"

echo ""
echo "3. Testing inter-service communication..."
echo "---------------------------------------"

test_endpoint "Global Summary (uses all services)" "http://localhost:8003/api/v1/reports/global-summary" "total_sales"
test_endpoint "Store Performances (uses stores API)" "http://localhost:8003/api/v1/reports/store-performances" "store_name"
test_endpoint "Top Products (uses products API)" "http://localhost:8003/api/v1/reports/top-products" "product_name"

echo ""
echo "4. Testing business operations..."
echo "-------------------------------"

# Test creating a sale (this will test communication between all services)
echo -n "Testing sale creation (inter-service communication)... "

sale_data='{
  "store_id": 1,
  "cash_register_id": 1,
  "lines": [
    {
      "product_id": 1,
      "quantite": 2,
      "prix_unitaire": 1.20
    }
  ]
}'

if response=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$sale_data" \
  "http://localhost:8003/api/v1/sales/" 2>/dev/null); then
    
    if echo "$response" | grep -q '"id"'; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "Sale created successfully with inter-service validation"
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Response: $response"
    fi
else
    echo -e "${RED}❌ FAIL - No response${NC}"
fi

echo ""
echo "5. Testing data consistency..."
echo "----------------------------"

# Get a product from Products API and verify it appears in Reporting API
echo -n "Testing data consistency between services... "

product_response=$(curl -s "http://localhost:8001/api/v1/products/1" 2>/dev/null)
if echo "$product_response" | grep -q '"nom"'; then
    product_name=$(echo "$product_response" | grep -o '"nom":"[^"]*"' | cut -d'"' -f4)
    
    # Check if this product appears in top products with same name
    top_products=$(curl -s "http://localhost:8003/api/v1/reports/top-products" 2>/dev/null)
    if echo "$top_products" | grep -q "$product_name"; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "Data consistency verified: $product_name found in both services"
    else
        echo -e "${YELLOW}⚠️  WARNING${NC}"
        echo "Product exists in Products API but not in Reporting API top products"
    fi
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "Could not fetch product from Products API"
fi

echo ""
echo "======================================"
echo -e "${GREEN}🎉 Microservices Architecture Test Complete!${NC}"
echo ""
echo "Access points:"
echo "📊 Products API: http://localhost:8001/docs"
echo "🏪 Stores API: http://localhost:8002/docs"  
echo "📈 Reporting API: http://localhost:8003/docs"
echo ""
echo "To view real-time logs: make logs"
echo "To check service status: make status" 