# Guide Load Balancer - Configuration Multi-Instances

## Vue d'ensemble

Cette configuration utilise **Nginx comme load balancer** avec **2 instances API** pour améliorer la résilience et les performances sous charge élevée.

## Architecture

```
[Client] → [Nginx Load Balancer:8000] → [API-1:8000] + [API-2:8000]
                                      ↓
                                [Prometheus] → [Grafana]
```

## Démarrage de l'Infrastructure

### 1. Configuration Load-Balanced
```bash
# Démarrer les services load-balanced
docker-compose -f docker-compose.loadbalanced.yml up -d

# Démarrer le monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Vérification du Statut
```bash
# Vérifier que tous les conteneurs sont en cours d'exécution
docker ps

# Vérifier les logs Nginx
docker logs log430-nginx

# Vérifier les instances API
docker logs log430-api-1
docker logs log430-api-2
```

## Endpoints de Surveillance

| Service | URL | Description |
|---------|-----|-------------|
| Load Balancer | http://localhost:8000 | API via Nginx |
| API Instance 1 | http://log430-api-1:8000 | Direct (interne) |
| API Instance 2 | http://log430-api-2:8000 | Direct (interne) |
| Prometheus | http://localhost:9090 | Métriques |
| Grafana | http://localhost:3000 | Dashboard |

## Configuration Nginx

### Load Balancing
- **Algorithme**: Round-Robin (par défaut)
- **Health Checks**: Automatiques via upstream
- **Timeout**: 60s pour connexions/lecture

### Métriques Collectées
- **Agrégées**: Via load balancer (job: api-loadbalanced)
- **Par instance**: Directement depuis chaque API (job: api-instances)
- **Nginx**: Statut du load balancer

## Dashboard Grafana

### Panels Principaux
1. **API Status (Load Balancer)**: Statut du load balancer
2. **Instance Health Status**: Santé de chaque instance
3. **Active Instances**: Nombre d'instances opérationnelles
4. **Total Traffic Rate**: Trafic total et par instance
5. **Request Distribution**: Répartition des requêtes
6. **Response Time by Instance**: Latence par instance
7. **Error Rate by Instance**: Erreurs par instance
8. **Active Requests**: Requêtes actives par instance
9. **CPU/Memory Usage**: Ressources par instance

## Test de Charge

### Script K6 Load-Balanced
```bash
# Lancer le test de stress load-balanced
k6 run k6-tests/loadbalanced-stress-test.js
```

### Profil de Test
- **Phase 1**: 0 → 100 utilisateurs (1 min)
- **Phase 2**: 100 → 300 utilisateurs (2 min)
- **Phase 3**: 300 → 700 utilisateurs (2 min)
- **Phase 4**: 700 → 1000 utilisateurs (1 min)
- **Phase 5**: Ramp-down (30s)

## Comparaison avec Instance Unique

### Améliorations Attendues
- **Résilience**: Pas de crash complet si une instance échoue
- **Distribution**: Charge répartie sur 2 instances
- **Latence**: Réduction des temps de réponse
- **Throughput**: Capacité supérieure (théoriquement x2)

### Métriques de Comparaison
| Métrique | 1 Instance | 2 Instances (Attendu) |
|----------|------------|----------------------|
| Max Users | ~700 (crash) | >1000 |
| P95 Latency | 800ms+ | <500ms |
| Error Rate | 100% (crash) | <10% |
| Recovery | Manual | Automatique |

## Dépannage

### Problèmes Courants

#### Load Balancer Down
```bash
# Vérifier la configuration Nginx
docker exec log430-nginx nginx -t

# Redémarrer Nginx
docker restart log430-nginx
```

#### Instance API Non Disponible
```bash
# Vérifier les logs d'une instance
docker logs log430-api-1

# Redémarrer une instance spécifique
docker restart log430-api-1
```

#### Métriques Manquantes
```bash
# Vérifier la connectivité Prometheus
curl http://localhost:9090/targets

# Vérifier les métriques d'une instance
curl http://localhost:8000/metrics
```

### Configuration Réseau
```bash
# Vérifier le réseau Docker
docker network inspect log430-labo-04_app-network

# Tester la connectivité interne
docker exec prometheus ping log430-api-1
```

## Optimisations Possibles

### Configuration Nginx
- **Least Connections**: Répartition basée sur la charge
- **IP Hash**: Session affinity si nécessaire
- **Health Checks**: Monitoring actif des instances

### Scaling
- **3+ Instances**: Ajout d'instances supplémentaires
- **Auto-scaling**: Basé sur les métriques
- **Geographic Distribution**: Multi-région

## Nettoyage

```bash
# Arrêter tous les services
docker-compose -f docker-compose.loadbalanced.yml down
docker-compose -f docker-compose.monitoring.yml down

# Nettoyer les volumes (optionnel)
docker volume rm $(docker volume ls -q | grep log430)
```

## Prochaines Étapes

1. **Lancer les tests de charge** pour valider les améliorations
2. **Capturer les screenshots** Grafana pour comparaison
3. **Analyser les résultats** dans le document de performance
4. **Optimiser la configuration** selon les résultats 