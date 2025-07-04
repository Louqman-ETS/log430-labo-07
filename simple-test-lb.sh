#!/bin/bash

echo "=== TEST DE LOAD BALANCING ===
"
echo "30 requêtes pour tester la répartition round-robin"
echo ""

# Compter manuellement
instance1_count=0
instance2_count=0
instance3_count=0
total_success=0

for i in $(seq 1 30); do
    echo -n "Requête $i: "
    
    response=$(curl -s -m 5 -H "apikey: admin-api-key-12345" http://localhost:9000/inventory/)
    
    if echo "$response" | grep -q "inventory-api-1"; then
        echo "✅ inventory-api-1"
        instance1_count=$((instance1_count + 1))
        total_success=$((total_success + 1))
    elif echo "$response" | grep -q "inventory-api-2"; then
        echo "✅ inventory-api-2"
        instance2_count=$((instance2_count + 1))
        total_success=$((total_success + 1))
    elif echo "$response" | grep -q "inventory-api-3"; then
        echo "✅ inventory-api-3"
        instance3_count=$((instance3_count + 1))
        total_success=$((total_success + 1))
    else
        echo "❌ Erreur ou rate limit"
        echo "   Réponse: $response"
    fi
    
    sleep 0.3  # Pause pour éviter le rate limiting
done

echo ""
echo "=== RÉSULTATS ==="
echo "Total réussi: $total_success/30"
echo ""
echo "Distribution:"
echo "  inventory-api-1: $instance1_count requêtes"
echo "  inventory-api-2: $instance2_count requêtes" 
echo "  inventory-api-3: $instance3_count requêtes"
echo ""

# Vérifier l'équilibrage
if [ $total_success -gt 0 ]; then
    echo "Pourcentages:"
    if [ $total_success -gt 0 ]; then
        perc1=$((instance1_count * 100 / total_success))
        perc2=$((instance2_count * 100 / total_success))
        perc3=$((instance3_count * 100 / total_success))
        echo "  inventory-api-1: ${perc1}%"
        echo "  inventory-api-2: ${perc2}%"
        echo "  inventory-api-3: ${perc3}%"
    fi
    
    echo ""
    if [ $instance1_count -gt 0 ] && [ $instance2_count -gt 0 ] && [ $instance3_count -gt 0 ]; then
        echo "✅ Toutes les instances répondent - Load balancing fonctionnel"
    else
        echo "⚠️ Certaines instances ne répondent pas"
    fi
else
    echo "❌ Aucune requête réussie"
fi 