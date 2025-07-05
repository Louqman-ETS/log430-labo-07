# Système Multi-Magasins - Architecture Microservices - LOG430

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Kong Gateway](https://img.shields.io/badge/Kong-Gateway-orange.svg)](https://konghq.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io)

Architecture microservices complète pour la gestion multi-magasins avec API Gateway Kong, load balancing, monitoring et haute disponibilité.

## Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Architecture Microservices](#architecture-microservices)
- [Évolution du Projet](#évolution-du-projet)
- [Microservices](#microservices)
- [Kong API Gateway](#kong-api-gateway)
- [Load Balancing et Haute Disponibilité](#load-balancing-et-haute-disponibilité)
- [Monitoring et Métriques](#monitoring-et-métriques)
- [Documentation](#documentation)
- [Déploiement](#déploiement)
- [Tests de Performance](#tests-de-performance)
- [Installation et Configuration](#installation-et-configuration)
- [Utilisation](#utilisation)
- [Technologies Utilisées](#technologies-utilisées)

## Vue d'Ensemble

Système complet de gestion multi-magasins évoluant d'une architecture monolithique vers une architecture microservices haute performance avec API Gateway Kong.

### Objectifs de Performance
- **Charge** : 100+ utilisateurs simultanés
- **Latence** : p95 < 105ms
- **Disponibilité** : 99.9% uptime
- **Scalabilité** : Horizontale avec Kong Gateway

### Fonctionnalités Principales
- **4 Microservices** : Inventory, Ecommerce, Retail, Reporting
- **API Gateway** : Kong avec load balancing intelligent
- **Interface Web** : Application Flask responsive
- **Monitoring** : Prometheus + Grafana
- **Cache distribué** : Redis avec stratégies TTL
- **Logs centralisés** : Kong Gateway + structured logging

## Architecture Microservices

### Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE MICROSERVICES                           │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│   API GATEWAY   │   MICROSERVICES │   DONNÉES       │   MONITORING      │
│                 │                 │                 │                   │
│ • Kong Gateway  │ • Inventory API │ • PostgreSQL    │ • Prometheus      │
│ • Load Balancer │ • Ecommerce API │ • Redis Cache   │ • Grafana         │
│ • Rate Limiting │ • Retail API    │ • Logs Files    │ • Alerting        │
│ • Auth/Keys     │ • Reporting API │ • Volumes       │ • Dashboards      │
│ • Logging       │ • Auto Scale    │ • Clustering    │ • Metrics         │
│ • Port 8000     │ • Ports 8001-4  │ • Port 5432     │ • Port 3000       │
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
         ↑                   ↑               ↑               ↑
    Client Requests     Domain Services  Persistent Data   Observability
      (HTTP/HTTPS)      (Independent)    (Shared/Isolated)  (Real-time)
```

### Microservices Domain Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DOMAINES MÉTIER                                  │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│   INVENTORY     │   ECOMMERCE     │    RETAIL       │   REPORTING       │
│                 │                 │                 │                   │
│ • Products      │ • Customers     │ • Stores        │ • Analytics       │
│ • Categories    │ • Orders        │ • Cash Registers│ • KPIs            │
│ • Stock Levels  │ • Carts         │ • Sales Trans.  │ • Dashboards      │
│ • Suppliers     │ • Payments      │ • Returns       │ • Trends          │
│ • Warehouses    │ • Shipping      │ • Inventory     │ • Forecasting     │
│                 │                 │                 │                   │
│ Port: 8001      │ Port: 8002      │ Port: 8003      │ Port: 8004        │
│ DB: inventory   │ DB: ecommerce   │ DB: retail      │ DB: reporting     │
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
         ↑                   ↑               ↑               ↑
    Product Catalog     Customer Journey   POS Operations   Business Intel
```

## Évolution du Projet

### Phase 1 - Lab 3 : Architecture Monolithique
- **Flask Web App** : Interface utilisateur complète
- **FastAPI** : API RESTful avec DDD
- **PostgreSQL** : Base de données partagée
- **Docker** : Containerisation de base

### Phase 2 - Lab 4 : Load Balancing et Cache
- **Nginx Load Balancer** : Distribution de charge
- **Redis Cache** : Optimisation des performances
- **Multiple Instances** : Scalabilité horizontale
- **Monitoring** : Métriques de base

### Phase 3 - Lab 5 : Microservices avec Kong Gateway
- **Kong Gateway** : API Gateway centralisé
- **4 Microservices** : Séparation par domaine
- **Prometheus + Grafana** : Monitoring avancé
- **Logging centralisé** : Traçabilité complète
- **API Key Management** : Sécurité et rate limiting

## Microservices

### 1. Inventory API (Port 8001)
**Domaine** : Gestion des produits et stocks
```yaml
Endpoints:
  - GET /api/v1/products
  - GET /api/v1/categories
  - GET /api/v1/stock
  - POST /api/v1/products
  - PUT /api/v1/stock/{product_id}

Responsabilités:
  - Catalogue produits
  - Gestion des catégories
  - Niveaux de stock
  - Réapprovisionnement
```

### 2. Ecommerce API (Port 8002)
**Domaine** : Gestion des clients et commandes
```yaml
Endpoints:
  - GET /api/v1/customers
  - GET /api/v1/orders
  - GET /api/v1/carts
  - POST /api/v1/orders
  - PUT /api/v1/carts/{cart_id}

Responsabilités:
  - Gestion clients
  - Commandes en ligne
  - Paniers d'achats
  - Processus de paiement
```

### 3. Retail API (Port 8003)
**Domaine** : Gestion des magasins et ventes
```yaml
Endpoints:
  - GET /api/v1/stores
  - GET /api/v1/cash-registers
  - GET /api/v1/sales
  - POST /api/v1/sales
  - POST /api/v1/returns

Responsabilités:
  - Gestion magasins
  - Caisses enregistreuses
  - Transactions de vente
  - Retours produits
```

### 4. Reporting API (Port 8004)
**Domaine** : Rapports et analytics
```yaml
Endpoints:
  - GET /api/v1/reports/sales
  - GET /api/v1/reports/inventory
  - GET /api/v1/reports/performance
  - GET /api/v1/analytics/trends
  - GET /api/v1/dashboards

Responsabilités:
  - Rapports métier
  - Analyses de performance
  - Tableaux de bord
  - Prévisions
```

## Kong API Gateway

### Configuration Load Balancée

Kong Gateway distribue intelligemment le trafic entre les instances des microservices avec load balancing avancé.

```yaml
# kong/kong-loadbalanced.yml
_format_version: "3.0"
_transform: true

services:
  - name: inventory-service
    url: http://inventory-1:8001
    tags: ["inventory"]
    routes:
      - name: inventory-route
        paths: ["/api/v1/products", "/api/v1/categories", "/api/v1/stock"]
        
  - name: ecommerce-service
    url: http://ecommerce-1:8002
    tags: ["ecommerce"]
    routes:
      - name: ecommerce-route
        paths: ["/api/v1/customers", "/api/v1/orders", "/api/v1/carts"]

upstreams:
  - name: inventory-upstream
    targets:
      - target: inventory-1:8001
        weight: 100
      - target: inventory-2:8001
        weight: 100
    healthchecks:
      active:
        http_path: "/health"
        healthy:
          interval: 30
          successes: 2
        unhealthy:
          interval: 10
          http_failures: 3
```

### Plugins Kong Configurés

#### 1. Rate Limiting
```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
      policy: local
      fault_tolerant: true
```

#### 2. Logging
```yaml
plugins:
  - name: file-log
    config:
      path: /var/log/kong/access.log
      reopen: true
```

#### 3. Prometheus Metrics
```yaml
plugins:
  - name: prometheus
    config:
      per_consumer: true
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
```

#### 4. Key Authentication
```yaml
plugins:
  - name: key-auth
    config:
      key_names: ["X-API-Key"]
      key_in_body: false
      key_in_header: true
      key_in_query: false
```

### Consumers et API Keys

```yaml
consumers:
  - username: admin-user
    keyauth_credentials:
      - key: "admin-key-12345"
    plugins:
      - name: rate-limiting
        config:
          minute: 1000
          
  - username: frontend-app
    keyauth_credentials:
      - key: "frontend-key-67890"
    plugins:
      - name: rate-limiting
        config:
          minute: 500
```

## Load Balancing et Haute Disponibilité

### Stratégies de Load Balancing

#### 1. Kong Gateway Level
- **Weighted Round Robin** : Distribution intelligente basée sur les poids
- **Health Checks** : Vérification automatique de la santé des instances
- **Circuit Breaker** : Protection contre les défaillances en cascade
- **Failover** : Basculement automatique vers instances saines

#### 2. Service Level
- **Multiple Instances** : 2-3 instances par microservice
- **Auto Scaling** : Ajustement automatique basé sur la charge
- **Resource Limits** : Isolation des ressources par container
- **Graceful Shutdown** : Arrêt propre avec drain des connexions

### Configuration Haute Disponibilité

```yaml
# docker-compose.kong.loadbalanced.yml
version: '3.8'

services:
  kong:
    image: kong:3.4.0
    environment:
      - KONG_DATABASE=off
      - KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml
      - KONG_ADMIN_ACCESS_LOG=/dev/stdout
      - KONG_ADMIN_ERROR_LOG=/dev/stderr
      - KONG_ADMIN_LISTEN=0.0.0.0:8001
      - KONG_PROXY_ACCESS_LOG=/dev/stdout
      - KONG_PROXY_ERROR_LOG=/dev/stderr
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "kong", "health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Microservices avec multiple instances
  inventory-1:
    build: ./services/inventory-api
    environment:
      - INSTANCE_ID=inventory-1
      - DATABASE_URL=postgresql://user:pass@db:5432/inventory
      - REDIS_URL=redis://redis:6379
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  inventory-2:
    build: ./services/inventory-api
    environment:
      - INSTANCE_ID=inventory-2
      - DATABASE_URL=postgresql://user:pass@db:5432/inventory
      - REDIS_URL=redis://redis:6379
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Monitoring et Métriques

### Stack de Monitoring

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MONITORING STACK                                   │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│   COLLECTION    │   STORAGE       │   VISUALIZATION │   ALERTING        │
│                 │                 │                 │                   │
│ • Kong Metrics  │ • Prometheus    │ • Grafana       │ • Alert Manager  │
│ • App Metrics   │ • Time Series   │ • Dashboards    │ • Slack/Email    │
│ • Logs          │ • Retention     │ • Real-time     │ • PagerDuty      │
│ • Health Checks │ • Clustering    │ • Custom Views  │ • Webhooks       │
│ • Custom        │ • Backup        │ • Mobile        │ • Escalation     │
│                 │                 │                 │                   │
│ Port: 9090      │ Port: 9090      │ Port: 3000      │ Port: 9093        │
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
         ↑                   ↑               ↑               ↑
    Scraping Endpoints   Metrics Storage   User Interface   Notifications
      (Every 15s)        (15 day retention) (Dashboard)    (Critical Events)
```

### Métriques Clés

#### Kong Gateway Metrics
```yaml
# Performances
- kong_request_duration_ms
- kong_request_count
- kong_response_size_bytes
- kong_upstream_latency_ms

# Santé
- kong_upstream_health_checks_total
- kong_upstream_health_check_failures_total
- kong_upstream_target_health

# Trafic
- kong_requests_per_second
- kong_bandwidth_bytes
- kong_rate_limiting_triggered_total
```

#### Application Metrics
```yaml
# FastAPI
- fastapi_requests_total
- fastapi_request_duration_seconds
- fastapi_requests_exceptions_total
- fastapi_requests_processing_time_seconds

# Business
- total_orders_created
- total_products_sold
- inventory_low_stock_alerts
- average_order_value
```

### Dashboards Grafana

#### 1. Kong Gateway Overview
- **Request Rate** : Requêtes par seconde
- **Latency Distribution** : P50, P95, P99
- **Error Rate** : Taux d'erreurs 4xx/5xx
- **Upstream Health** : État des services backend

#### 2. Microservices Performance
- **Response Times** : Temps de réponse par service
- **Throughput** : Débit par endpoint
- **Resource Usage** : CPU, Memory, Network
- **Database Connections** : Pool de connexions

#### 3. Business Metrics
- **Sales Performance** : Ventes temps réel
- **Inventory Levels** : Niveaux de stock
- **Customer Activity** : Activité client
- **System Health** : Santé globale du système

## Documentation

### Documentation Technique

#### 1. Architecture Documentation
- **[Rapport Arc42](docs/rapport-arc42/rapport-arc42-microservices.md)** : Architecture complète
- **[Vues 4+1](docs/docs4+1/)** : Diagrammes PlantUML
- **[ADR](docs/ADR/)** : Décisions architecturales

#### 2. Documentation API
- **OpenAPI Specs** : Documentation automatique par service
- **Postman Collection** : Tests et exemples d'utilisation
- **Kong Admin API** : Configuration et gestion

#### 3. Guides Opérationnels
- **[Performance Analysis](docs/monitoring/PERFORMANCE_ANALYSIS.md)** : Analyses de performance
- **[Load Balancer Guide](docs/monitoring/kong-load-balancer-test-report.md)** : Guide du load balancer
- **[Monitoring Guide](docs/monitoring/)** : Configuration monitoring

### Documentation Générée

```bash
# Génération OpenAPI
python scripts/generate_openapi_spec.py

# Documentation PlantUML
plantuml docs/docs4+1/*.puml

# Rapport Arc42
# Voir docs/rapport-arc42/rapport-arc42-microservices.md
```

## Déploiement

### Déploiement Local

#### 1. Setup complet avec Kong Gateway
```bash
# Clone du projet
git clone <repository-url>
cd log430-labo-05

# Démarrage avec Kong Gateway et Load Balancing
make kong-loadbalanced-up

# Ou avec Docker Compose
docker-compose -f docker-compose.kong.loadbalanced.yml up -d
```

#### 2. Vérification des Services
```bash
# Kong Gateway
curl -X GET http://localhost:8000/api/v1/products \
  -H "X-API-Key: admin-key-12345"

# Monitoring
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

### Commandes Makefile

```bash
# Gestion Kong Load Balancé
make kong-loadbalanced-up           # Démarrage complet
make kong-loadbalanced-down         # Arrêt complet
make kong-loadbalanced-logs         # Logs des services
make kong-loadbalanced-status       # État des services

# Tests et monitoring
make test-loadbalancing             # Tests de load balancing
make test-performance               # Tests de performance
make monitoring-up                  # Démarrage monitoring
```

### Configuration Environnements

#### Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  kong:
    image: kong:3.4.0
    environment:
      - KONG_DATABASE=postgres
      - KONG_PG_HOST=postgres
      - KONG_PG_DATABASE=kong
      - KONG_PG_USER=kong
      - KONG_PG_PASSWORD=${KONG_DB_PASSWORD}
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

#### Development
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  kong:
    image: kong:3.4.0
    environment:
      - KONG_DATABASE=off
      - KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml
      - KONG_LOG_LEVEL=debug
    volumes:
      - ./logs:/var/log/kong
    ports:
      - "8001:8001"  # Admin API
```

## Tests de Performance

### Suite de Tests K6

#### 1. Test de Charge Standard
```javascript
// k6-tests/medium-load-test.js
import { check, sleep } from 'k6';
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '2m', target: 50 },   // Montée progressive
    { duration: '5m', target: 100 },  // Maintien charge
    { duration: '2m', target: 0 },    // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<105'],  // 95% < 105ms
    http_req_failed: ['rate<0.1'],     // <10% d'erreurs
  },
};

export default function() {
  const response = http.get('http://localhost:8000/api/v1/products', {
    headers: { 'X-API-Key': 'admin-key-12345' },
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 105ms': (r) => r.timings.duration < 105,
  });
  
  sleep(1);
}
```

#### 2. Test de Stress
```javascript
// k6-tests/loadbalanced-stress-test.js
export let options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 300 },  // Stress test
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.05'],
  },
};
```

### Résultats de Performance

#### Benchmarks Atteints
```
Configuration: Kong Gateway + 3 instances par service
Charge: 300 utilisateurs simultanés
Durée: 20 minutes

Résultats:
✓ Latence P95: 95ms (objectif: <105ms)
✓ Taux d'erreur: 0.02% (objectif: <1%)
✓ Throughput: 1,200 req/s
✓ Disponibilité: 99.98%
```

#### Comparaison des Configurations
```
Single Instance:
- P95 Latency: 150ms
- Max Throughput: 400 req/s
- Memory Usage: 1.2GB

Load Balanced (3 instances):
- P95 Latency: 95ms
- Max Throughput: 1,200 req/s
- Memory Usage: 3.6GB (distributed)
```

## Installation et Configuration

### Prérequis

```bash
# Système requis
- Docker 24.0+
- Docker Compose 2.0+
- Python 3.11+
- Node.js 18+ (pour les tests)
- Make (pour les commandes)

# Installation des outils
npm install -g k6              # Tests de performance
pip install -r requirements.txt # Dépendances Python
```

### Configuration Initiale

#### 1. Variables d'Environnement
```bash
# .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=multi_stores
REDIS_URL=redis://localhost:6379
KONG_ADMIN_URL=http://localhost:8001
```

#### 2. Configuration Kong
```bash
# Configuration initiale Kong
./kong/configure-kong.sh

# Application de la configuration
./kong/apply-config.sh
```

#### 3. Initialisation des Données
```bash
# Génération des données de test
python services/generate_test_data.py

# Initialisation des bases de données
docker-compose exec inventory-1 python src/init_db.py
docker-compose exec ecommerce-1 python src/init_db.py
docker-compose exec retail-1 python src/init_db.py
docker-compose exec reporting-1 python src/init_db.py
```

## Utilisation

### Accès aux Services

#### Kong Gateway (API Principal)
```bash
# Base URL
http://localhost:8000

# Exemples d'utilisation
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "X-API-Key: admin-key-12345"

curl -X GET "http://localhost:8000/api/v1/stores" \
  -H "X-API-Key: frontend-key-67890"
```

#### Interface Web Flask
```bash
# URL
http://localhost:8080

# Fonctionnalités
- Dashboard multi-magasins
- Gestion des ventes
- Rapports et analytics
- Gestion des stocks
```

#### Monitoring
```bash
# Grafana
http://localhost:3000
User: admin / Password: admin

# Prometheus
http://localhost:9090
```

### API Endpoints Principaux

#### Inventory Service
```bash
GET    /api/v1/products         # Liste des produits
POST   /api/v1/products         # Créer un produit
GET    /api/v1/categories       # Liste des catégories
GET    /api/v1/stock           # Niveaux de stock
PUT    /api/v1/stock/{id}      # Mise à jour stock
```

#### Ecommerce Service
```bash
GET    /api/v1/customers        # Liste des clients
POST   /api/v1/customers        # Créer un client
GET    /api/v1/orders          # Liste des commandes
POST   /api/v1/orders          # Créer une commande
GET    /api/v1/carts           # Paniers d'achats
```

#### Retail Service
```bash
GET    /api/v1/stores           # Liste des magasins
POST   /api/v1/stores           # Créer un magasin
GET    /api/v1/cash-registers   # Caisses enregistreuses
GET    /api/v1/sales            # Transactions de vente
POST   /api/v1/sales            # Nouvelle vente
```

#### Reporting Service
```bash
GET    /api/v1/reports/sales    # Rapports de ventes
GET    /api/v1/reports/inventory # Rapports d'inventaire
GET    /api/v1/analytics/trends # Analyses de tendances
GET    /api/v1/dashboards       # Tableaux de bord
```

## Technologies Utilisées

### Backend
- **FastAPI 0.104.1** : Framework API moderne et performant
- **Python 3.11** : Langage principal
- **PostgreSQL 15** : Base de données relationnelle
- **Redis 7.0** : Cache distribué et sessions
- **SQLAlchemy 2.0** : ORM moderne avec async support

### API Gateway et Load Balancing
- **Kong Gateway 3.4.0** : API Gateway et load balancer
- **Nginx** : Proxy inverse et load balancing
- **Docker Compose** : Orchestration des services
- **Kong Plugins** : Rate limiting, logging, metrics

### Monitoring et Observabilité
- **Prometheus** : Collecte de métriques
- **Grafana** : Visualisation et dashboards
- **Structured Logging** : Logs JSON structurés
- **Health Checks** : Monitoring de santé des services

### Tests et Qualité
- **K6** : Tests de performance et charge
- **Pytest** : Tests unitaires et d'intégration
- **Coverage** : Couverture de tests
- **Postman** : Tests API et documentation

### Frontend
- **Flask 3.0.0** : Framework web Python
- **Jinja2** : Moteur de templates
- **Bootstrap 5** : Framework CSS responsive
- **JavaScript ES6** : Interactivité côté client

### DevOps et Infrastructure
- **Docker** : Containerisation
- **Docker Compose** : Orchestration locale
- **Makefile** : Automatisation des tâches
- **Git** : Gestion de versions

### Documentation
- **OpenAPI/Swagger** : Documentation API automatique
- **PlantUML** : Diagrammes d'architecture
- **Arc42** : Template de documentation architecturale
- **Markdown** : Documentation technique

---

## Qualité de Code

### Outils de Développement

Ce projet utilise des outils de qualité de code pour maintenir un style cohérent :

- **Black 24.4.2** : Formatage automatique du code Python
- **isort** : Tri et organisation des imports  
- **flake8** : Linting et vérification du style
- **bandit** : Analyse de sécurité
- **safety** : Vérification des vulnérabilités

### Commandes Makefile

```bash
# Formatage complet
make lint-all

# Commandes individuelles
make format        # Formater avec black
make sort-imports  # Trier les imports
make lint          # Vérifier avec flake8
make check-format  # Vérifier sans modifier
```

### Utilisation Manuelle

```bash
# Formatage du code
python -m black --line-length 88 .

# Tri des imports
python -m isort --profile=black .

# Vérification du style
python -m flake8 --max-line-length=88 --extend-ignore=E203,W503 .
```

## Contributeurs

- **Louqman Masbahi** : Architecture et développement
- **Instructeurs** : Guidance et reviews architecturales

## Licence

Ce projet est développé dans le cadre du cours LOG430 - Architecture et Conception de Logiciels.
