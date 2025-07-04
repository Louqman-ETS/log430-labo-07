## Configuration Kong - Architecture DDD

Cette configuration Kong est optimisée pour une architecture Domain-Driven Design (DDD) avec des microservices spécialisés.

### **Routage dynamique**
- Routes configurées par domaine métier
- Préfixes clairs : `/inventory`, `/ecommerce`, `/retail`, `/reporting`
- Load balancing automatique avec health checks
- Gestion des erreurs et timeouts

### **Clés API**
- Authentification par clés API
- Différents niveaux d'accès (admin, frontend, mobile, partners)
- Rate limiting par consommateur
- Logging des accès pour audit

### **Logging centralisé**
- Logs structurés avec Request-ID
- Tracking des performances par service
- Métriques Prometheus intégrées
- Observabilité complète

## Démarrage rapide

### 1. Démarrer Kong
```bash
# Démarrer Kong avec la base de données
make -f Makefile.kong kong-up

# Vérifier que Kong fonctionne
curl -s http://localhost:9001/status | jq
```

### 2. Configurer les services
```bash
# Appliquer la configuration DDD
chmod +x kong/configure-kong.sh
./kong/configure-kong.sh

# Tester la configuration
chmod +x kong/test-kong.sh
./kong/test-kong.sh
```

### 3. Tester les endpoints
```bash
# Test avec clé API
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/inventory/api/v1/products/

# Test des autres services
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/ecommerce/api/v1/customers/
```

## Clés API disponibles

| Consommateur | Clé API | Usage |
|-------------|---------|-------|
| admin-user | `admin-api-key-12345` | Administration complète |
| frontend-app | `frontend-api-key-67890` | Application web frontend |
| mobile-app | `mobile-api-key-abcde` | Application mobile |
| external-partner | `partner-api-key-fghij` | Partenaires externes |

### Utilisation des clés API

```bash
# Header HTTP
curl -H "apikey: admin-api-key-12345" http://localhost:9000/inventory/

# Query parameter (moins sécurisé)
curl "http://localhost:9000/inventory/?apikey=admin-api-key-12345"
```

## Services et Routes

| Service | Route | Port Backend | Description |
|---------|-------|-------------|-------------|
| inventory-api | `/inventory` | 8001 | Gestion produits et stock |
| ecommerce-api | `/ecommerce` | 8000 | Clients, paniers, commandes |
| retail-api | `/retail` | 8002 | Magasins, caisses, ventes |
| reporting-api | `/reporting` | 8005 | Rapports et analytics |

### Exemples d'endpoints

```bash
# Inventory API
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/inventory/api/v1/products/

# Ecommerce API
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/ecommerce/api/v1/customers/

# Retail API
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/retail/api/v1/stores/

# Reporting API
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/reporting/api/v1/reports/
```

## Plugins Configurés

### Rate Limiting
- **Limite** : 100 requêtes par minute par consommateur
- **Fenêtre** : 1 minute
- **Politique** : Par clé API

### Prometheus Metrics
- **Métriques** : Requêtes, latence, erreurs
- **Endpoint** : http://localhost:9001/metrics
- **Grafana** : Dashboard automatique

### Request ID
- **Header** : `X-Request-ID`
- **Génération** : UUID automatique
- **Propagation** : Vers tous les services

## Configuration avancée

### Load Balancing
```bash
# Ajouter des instances pour inventory-api
curl -X POST http://localhost:9001/upstreams/inventory-api-upstream/targets \
  -H "Content-Type: application/json" \
  -d '{"target": "inventory-api-2:8001", "weight": 100}'

# Vérifier la distribution
curl -s http://localhost:9001/upstreams/inventory-api-upstream/targets | jq
```

### Health Checks
```bash
# Vérifier la santé des services
curl -s http://localhost:9001/upstreams/inventory-api-upstream/health | jq
```

## Commandes utiles

```bash
# Voir tous les services
curl -s http://localhost:9001/services | jq '.data[] | {name: .name, url: .url}'

# Voir toutes les routes
curl -s http://localhost:9001/routes | jq '.data[] | {name: .name, paths: .paths}'

# Voir les consommateurs
curl -s http://localhost:9001/consumers | jq '.data[] | {username: .username}'

# Nettoyage complet (supprime toutes les données)
make -f Makefile.kong kong-clean
```

### Debugging
```bash
# Logs Kong
docker logs -f kong-gateway

# Logs base de données Kong
docker logs -f kong-database

# Tester la connectivité
curl -v http://localhost:9000/inventory/api/v1/products/
```

### Monitoring
```bash
# Métriques Prometheus
curl -s http://localhost:9001/metrics | grep kong_http_requests_total

# Statut des services
curl -s http://localhost:9001/status | jq

# Informations sur Kong
curl -s http://localhost:9001/ | jq
```

## Architecture

```
Frontend/Mobile Apps
         ↓
    Kong Gateway (9000)
         ↓
   ┌─────────────────┐
   │   Load Balancer │
   └─────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│                  Services                        │
├─────────────────────────────────────────────────┤
│ inventory-api:8001  │  ecommerce-api:8000       │
│ retail-api:8002     │  reporting-api:8005       │
└─────────────────────────────────────────────────┘
         ↓
    PostgreSQL DBs
```

## Avantages de cette architecture

### **Point d'entrée unique**
- Une seule URL pour tous les services
- Gestion centralisée des versions d'API
- Routage intelligent par domaine métier

### **Sécurité renforcée**
- Authentification centralisée
- Rate limiting par consommateur
- Logging complet des accès
- Validation des requêtes

### **Observabilité**
- Métriques Prometheus automatiques
- Request tracing avec X-Request-ID
- Logs structurés pour chaque service
- Monitoring des performances

### **Scalabilité**
- Load balancing automatique
- Health checks des instances
- Ajout d'instances à chaud
- Distribution équitable du trafic

Cette configuration est optimisée pour un environnement de production avec monitoring complet et haute disponibilité. 