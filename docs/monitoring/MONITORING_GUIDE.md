# Guide de Monitoring - API avec Load Balancer

## Démarrage rapide

### 1. Démarrer l'infrastructure complète
```bash
# Démarrer avec monitoring
make monitoring-up

# Ou démarrer séparément
make kong-up
make loadbalanced-up
make monitoring-up
```

### 2. Accéder aux dashboards
- **Grafana** : http://localhost:3000 (admin/admin)
- **Prometheus** : http://localhost:9090
- **Kong Admin** : http://localhost:9001

### 3. Lancer des tests de charge
```bash
# Test simple
./simple-test-lb.sh

# Test de stress K6
cd k6-tests
k6 run loadbalanced-stress-test.js
```

### 4. Observer les métriques
- Ouvrir Grafana → Dashboard "API Load Balancer Monitoring"
- Surveiller les graphiques en temps réel
- Analyser les performances par instance

### 5. Analyser les résultats
- Comparer les métriques avant/pendant/après les tests
- Identifier les goulots d'étranglement
- Optimiser la configuration

## Dashboard Grafana

Le dashboard "API Load Balancer Monitoring" inclut :

- **API Health** → Santé interne (si API accessible)
- **Request Rate** → Requêtes par seconde
- **Latency** → Temps de réponse (P50, P95, P99)
- **Error Rate** → Taux d'erreur par instance
- **Load Distribution** → Distribution des requêtes entre instances

## Tests de stress avec métriques

### Test K6 avec métriques
```bash
cd k6-tests
k6 run --out prometheus-remote-write=http://localhost:9090/api/v1/write loadbalanced-stress-test.js
```

### Test simple avec curl
```bash
# Test de charge basique
for i in {1..100}; do
  curl -s -H "apikey: admin-api-key-12345" \
    http://localhost:9000/inventory/api/v1/products/ \
    -w "Time: %{time_total}s, Status: %{http_code}\n" \
    -o /dev/null &
done
wait
```

### Monitoring en temps réel
```bash
# Surveiller les logs Kong
docker logs -f kong-gateway

# Surveiller les métriques système
docker stats

# Surveiller les instances API
docker logs -f inventory-api-1
docker logs -f inventory-api-2
docker logs -f inventory-api-3
```

## Comparaison avant/après améliorations

### Métriques à surveiller
1. **Latence moyenne** : Temps de réponse moyen
2. **Percentiles** : P95, P99 pour les requêtes les plus lentes
3. **Throughput** : Requêtes par seconde
4. **Taux d'erreur** : Pourcentage d'erreurs HTTP
5. **Distribution** : Équilibrage entre instances
6. **Resource usage** : CPU, mémoire par instance

### Exemple de comparaison
```
AVANT (1 instance) :
- Latence P95: 250ms
- Throughput: 50 req/s
- Taux d'erreur: 2%

APRÈS (3 instances + LB) :
- Latence P95: 80ms
- Throughput: 150 req/s
- Taux d'erreur: 0.1%
```

## Endpoints utiles

- **Métriques Prometheus** : http://localhost:9090/metrics
- **Santé Kong** : http://localhost:9001/status
- **Métriques Kong** : http://localhost:9001/metrics
- **APIs Kong** : http://localhost:9001/services

## Commandes utiles

```bash
# Redémarrer une instance spécifique
docker restart inventory-api-2

# Voir les métriques en temps réel
watch -n 1 'curl -s http://localhost:9001/metrics | grep kong_http_requests_total'

# Analyser les logs avec filtrage
docker logs inventory-api-1 2>&1 | grep "ERROR\|WARN"

# Vérifier la distribution des requêtes
docker logs kong-gateway 2>&1 | grep "upstream" | tail -20
``` 