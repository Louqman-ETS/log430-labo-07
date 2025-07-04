#!/bin/bash

echo "=== TEST DE LOAD BALANCING ===
"
echo "Test de répartition de charge entre 3 instances d'inventory-api"
echo "Algorithme: Round-Robin via Kong API Gateway"
echo ""

# Tableaux pour compter les instances
declare -A instance_count
total_requests=0
total_success=0

echo "Exécution de 30 requêtes avec pause de 0.2s entre chaque..."
echo ""

for i in {1..30}; do
    echo -n "Requête $i: "
    
    # Faire la requête avec timeout
    response=$(curl -s -m 5 -H "apikey: admin-api-key-12345" http://localhost:9000/inventory/)
    
    if [ $? -eq 0 ]; then
        # Extraire l'instance ID de la réponse JSON
        instance_id=$(echo "$response" | grep -o '"instance":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$instance_id" ]; then
            echo "✅ $instance_id"
            instance_count[$instance_id]=$((${instance_count[$instance_id]} + 1))
            total_success=$((total_success + 1))
        else
            echo "❌ Pas d'instance ID trouvé"
        fi
    else
        echo "❌ Erreur de connexion"
    fi
    
    total_requests=$((total_requests + 1))
    
    # Pause entre les requêtes pour éviter le rate limiting
    sleep 0.2
done

echo ""
echo "=== RÉSULTATS DU LOAD BALANCING ==="
echo "Total des requêtes: $total_requests"
echo "Requêtes réussies: $total_success"
echo "Taux de succès: $(echo "scale=1; $total_success * 100 / $total_requests" | bc -l)%"
echo ""

echo "Distribution par instance:"
for instance in "${!instance_count[@]}"; do
    count=${instance_count[$instance]}
    percentage=$(echo "scale=1; $count * 100 / $total_success" | bc -l)
    echo "  $instance: $count requêtes ($percentage%)"
done

echo ""

# Vérifier l'équilibrage
if [ ${#instance_count[@]} -eq 3 ]; then
    echo "✅ Les 3 instances répondent"
    
    # Calculer la déviation standard
    expected=$((total_success / 3))
    max_count=0
    min_count=999999
    
    for count in "${instance_count[@]}"; do
        if [ $count -gt $max_count ]; then
            max_count=$count
        fi
        if [ $count -lt $min_count ]; then
            min_count=$count
        fi
    done
    
    deviation=$((max_count - min_count))
    echo "Écart max-min: $deviation requêtes"
    
    if [ $deviation -le 2 ]; then
        echo "✅ Load balancing ÉQUILIBRÉ"
    else
        echo "⚠️ Load balancing légèrement déséquilibré"
    fi
else
    echo "❌ Toutes les instances ne répondent pas"
fi

echo ""
echo "=== TEST TERMINÉ ===" 