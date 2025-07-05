# Rapport Architecture ARC42 - Système Microservices Multi-Magasins
## Évolution Labs 3 à 5 - LOG430

**Auteur** : Louqman Masbahi  
**Date** : 05 juillet 2025 
**Version** : 5.0  
**Projet** : Architecture Microservices avec API Gateway et Observabilité  
**Évolution** : Lab 3 → Lab 4 → Lab 5

---

## 1. Introduction et Objectifs

### 1.1 Aperçu du Système

Ce rapport documente l'évolution architecturale d'une API monolithique FastAPI (Lab 3) vers une architecture microservices complète avec load balancing, caching et observabilité (Labs 4-5).

### 1.2 Objectifs Architecturaux

**Objectifs Fonctionnels :**
- Décomposer l'API monolithique en 4 microservices (Architecture DDD)
- Centraliser l'accès via Kong API Gateway
- Maintenir la cohérence des données avec des bases dédiées
- Fournir des APIs REST pour e-commerce, retail, inventaire et reporting

**Objectifs Non-Fonctionnels :**
- **Scalabilité** : Load balancing avec 3 instances Inventory API
- **Performance** : Support de 100+ utilisateurs simultanés, latence p95 < 105ms
- **Disponibilité** : 99.9% uptime avec monitoring Prometheus/Grafana
- **Maintenabilité** : Déploiements indépendants par microservice
- **Observabilité** : Métriques détaillées et alertes automatiques

### 1.3 Stakeholders

| Rôle | Responsabilités | Préoccupations |
|------|----------------|---------------|
| **Clients E-commerce** | Commandes en ligne | Performance, disponibilité des APIs |
| **Employés Magasin** | Ventes, gestion stock | Rapidité des transactions, cohérence stock |
| **Administrateurs** | Configuration système | Monitoring, performance, sécurité |
| **Équipe DevOps** | Déploiement, monitoring | Observabilité, scalabilité, maintenance |
| **Architecte Système** | Évolution technique | Cohérence architecture, dette technique |

---

## 2. Contraintes

### 2.1 Contraintes Techniques

- **Plateforme** : APIs REST avec FastAPI (Python 3.11)
- **Base de Données** : PostgreSQL avec bases dédiées par service
- **Communication** : HTTP/REST uniquement (pas de messaging)
- **Déploiement** : Docker Compose (infrastructure simplifiée)
- **API Gateway** : Kong Gateway pour routage et load balancing
- **Monitoring** : Prometheus + Grafana stack

### 2.2 Contraintes Organisationnelles

- **Équipe** : Équipe unique gérant tous les microservices
- **Budget** : Infrastructure Docker simple (pas de Kubernetes)
- **Délai** : Migration progressive sur 3 phases (Lab 3→4→5)
- **Compétences** : Montée en compétences sur architecture microservices

### 2.3 Contraintes Règlementaires

- **Audit** : Traçabilité des transactions et modifications de stock
- **Sécurité** : Authentification et autorisation centralisées

---

## 3. Contexte

### 3.1 Contexte Métier

**Domaine** : E-commerce et retail multi-magasins  
**Modèle** : Plateforme unifiée pour ventes online et en magasin  
**Enjeux** : Performance, scalabilité, observabilité des systèmes

### 3.2 Évolution Lab 3 → Lab 5

#### Lab 3 : API RESTful Monolithique
```
[Client] ↔ [API FastAPI Monolithique] ↔ [PostgreSQL]
```
- API FastAPI unique avec tous les endpoints
- Base de données centralisée
- Architecture simple mais non scalable

#### Lab 4 : Load Balancing et Caching
```
[Client] ↔ [Load Balancer] ↔ [Multiple API Instances] ↔ [PostgreSQL + Redis]
```
- Load balancer Nginx
- Multiple instances d'API
- Cache Redis pour performance
- Monitoring basique

#### Lab 5 : Architecture Microservices avec Kong
```
[Client] ↔ [Kong Gateway] ↔ [4 Microservices] ↔ [4 PostgreSQL Databases]
                    ↓
            [Prometheus + Grafana]
```
- 4 microservices indépendants
- Kong Gateway avec load balancing intégré
- Bases de données dédiées par service
- Observabilité complète

### 3.3 Contraintes d'Évolution

**Éléments à Conserver :**
- Logique métier existante (ventes, gestion stock, commandes)
- Modèles de données essentiels
- Compatibilité API pour les clients

**Éléments à Modifier :**
- Architecture monolithique → microservices
- Base unique → bases dédiées
- Load balancer simple → Kong Gateway

**Éléments à Ajouter :**
- API Gateway centralisé
- Monitoring et observabilité
- Métriques de performance

---

## 4. Stratégie de Solution

### 4.1 Approche Architecturale

**Principe Directeur** : *Domain-Driven Microservices*

Nous avons adopté une approche **Domain-Driven Design (DDD)** pour décomposer le monolithe en 4 microservices alignés sur les domaines métier.

### 4.2 Patterns Architecturaux Appliqués

1. **Microservices Pattern** : Décomposition par domaine métier
2. **API Gateway Pattern** : Point d'entrée unique avec Kong
3. **Database per Service** : Isolation des données par microservice
4. **Load Balancer Pattern** : Répartition de charge sur Inventory API
5. **Observability Pattern** : Monitoring centralisé Prometheus/Grafana

### 4.3 Analyse Domain-Driven Design

#### Identification des Bounded Contexts

**Référence** : Cette analyse DDD est reflétée dans la documentation 4+1 :
- **Vue Logique** : Modèle de domaine par microservice
- **Vue Processus** : Interactions entre domaines
- **Vue Développement** : Structure des composants

**1. Bounded Context : Inventory Management**
```
Microservice: Inventory API (3 instances load-balancées)
Port: 8001
Database: inventory_db (Port 5433)
- Entities: Product, Category, StockMovement, StockAlert
- Endpoints: /products, /categories, /stock
- Responsabilités: Gestion produits, catégories, stocks, alertes
```

**2. Bounded Context : E-commerce**
```
Microservice: Ecommerce API (1 instance)
Port: 8000
Database: ecommerce_db (Port 5450)
- Entities: Customer, Cart, Order, Address
- Endpoints: /customers, /carts, /orders
- Responsabilités: Clients, paniers, commandes, authentification
```

**3. Bounded Context : Retail Operations**
```
Microservice: Retail API (1 instance)
Port: 8002
Database: retail_db (Port 5434)
- Entities: Store, CashRegister, Sale, SaleLine
- Endpoints: /stores, /cash-registers, /sales
- Responsabilités: Magasins, caisses, ventes physiques
```

**4. Bounded Context : Business Intelligence**
```
Microservice: Reporting API (1 instance)
Port: 8003
Database: reporting_db (Port 5435)
- Entities: Report, Analytics
- Endpoints: /reports, /analytics
- Responsabilités: Rapports, analyses, agrégations
```

#### Relations entre Bounded Contexts

**Référence** : Documentées dans les diagrammes de séquence (Vue Processus)

- **Commandes E-commerce** : Ecommerce → Inventory (validation stock)
- **Ventes Retail** : Retail → Inventory (réduction stock)
- **Reporting** : Reporting → All Services (agrégation données)

---

## 5. Vue des Blocs de Construction

### 5.1 Architecture Microservices Complète

**Référence** : Vue Développement `docs/docs4+1/vue-developpement.puml`


#### Diagramme Architecture - Vue Développement

```plantuml
@startuml vue-developpement
!theme plain

title Documentation 4+1 - Vue Développement

package "Kong Gateway" {
    component "Kong Core" as Kong
    component "Load Balancer" as LB
    component "API Gateway" as Gateway
    component "Service Discovery" as Discovery
    component "Rate Limiting" as RateLimit
    component "Authentication" as Auth
    
    Kong ..> LB
    Kong ..> Gateway
    Kong ..> Discovery
    Kong ..> RateLimit
    Kong ..> Auth
}

package "Monitoring & Observability" {
    component "Prometheus" as Prometheus
    component "Grafana" as Grafana
    component "Metrics Collector" as Metrics
    
    Prometheus ..> Metrics
    Grafana ..> Prometheus
}

package "Ecommerce API (Port 8000)" {
    component "Customer Service" as CustomerService
    component "Cart Service" as CartService
    component "Order Service" as OrderService
    component "Authentication Service" as AuthService
    component "Address Service" as AddressService
    
    package "Ecommerce Infrastructure" {
        component "FastAPI Framework" as EcommerceAPI
        component "SQLAlchemy ORM" as EcommerceORM
        component "Pydantic Schemas" as EcommerceSchemas
        component "JWT Auth" as JWTAuth
        component "Password Hashing" as PasswordHash
        database "PostgreSQL" as EcommerceDB
    }
    
    CustomerService ..> EcommerceORM
    CartService ..> EcommerceORM
    OrderService ..> EcommerceORM
    AuthService ..> JWTAuth
    AuthService ..> PasswordHash
    AddressService ..> EcommerceORM
    
    EcommerceAPI ..> EcommerceSchemas
    EcommerceORM ..> EcommerceDB
}

package "Inventory API (Port 8001)" {
    component "Product Service" as ProductService
    component "Category Service" as CategoryService
    component "Stock Service" as StockService
    component "Stock Alert Service" as StockAlertService
    component "Stock Movement Service" as StockMovementService
    
    package "Inventory Infrastructure" {
        component "FastAPI Framework" as InventoryAPI
        component "SQLAlchemy ORM" as InventoryORM
        component "Pydantic Schemas" as InventorySchemas
        component "Logging Service" as InventoryLogging
        database "PostgreSQL" as InventoryDB
    }
    
    ProductService ..> InventoryORM
    CategoryService ..> InventoryORM
    StockService ..> InventoryORM
    StockAlertService ..> InventoryORM
    StockMovementService ..> InventoryORM
    
    InventoryAPI ..> InventorySchemas
    InventoryORM ..> InventoryDB
}

package "Retail API (Port 8002)" {
    component "Store Service" as StoreService
    component "Cash Register Service" as CashRegisterService
    component "Sale Service" as SaleService
    component "Sale Line Service" as SaleLineService
    component "Store Metrics Service" as StoreMetricsService
    
    package "Retail Infrastructure" {
        component "FastAPI Framework" as RetailAPI
        component "SQLAlchemy ORM" as RetailORM
        component "Pydantic Schemas" as RetailSchemas
        component "External Service Client" as RetailClient
        database "PostgreSQL" as RetailDB
    }
    
    StoreService ..> RetailORM
    CashRegisterService ..> RetailORM
    SaleService ..> RetailORM
    SaleLineService ..> RetailORM
    StoreMetricsService ..> RetailORM
    
    RetailAPI ..> RetailSchemas
    RetailORM ..> RetailDB
    SaleService ..> RetailClient
}

package "Reporting API (Port 8003)" {
    component "Report Service" as ReportService
    component "Analytics Service" as AnalyticsService
    component "Data Aggregation Service" as DataAggregationService
    component "Export Service" as ExportService
    
    package "Reporting Infrastructure" {
        component "FastAPI Framework" as ReportingAPI
        component "SQLAlchemy ORM" as ReportingORM
        component "Pydantic Schemas" as ReportingSchemas
        component "External Service Client" as ReportingClient
        component "Data Synchronization" as DataSync
        database "PostgreSQL" as ReportingDB
    }
    
    ReportService ..> ReportingORM
    AnalyticsService ..> ReportingORM
    DataAggregationService ..> ReportingClient
    ExportService ..> ReportingORM
    
    ReportingAPI ..> ReportingSchemas
    ReportingORM ..> ReportingDB
    DataAggregationService ..> DataSync
}

' Relations inter-services (via HTTP/REST)
Kong ..> EcommerceAPI : routes
Kong ..> InventoryAPI : routes
Kong ..> RetailAPI : routes
Kong ..> ReportingAPI : routes

' Dependances externes des services
OrderService ..> Kong : calls_inventory
SaleService ..> Kong : calls_inventory
ReportingClient ..> Kong : calls_all_apis

' Monitoring
EcommerceAPI ..> Metrics : exports
InventoryAPI ..> Metrics : exports
RetailAPI ..> Metrics : exports
ReportingAPI ..> Metrics : exports

note top of Kong
Point d'entree unique
Load Balancing
API Gateway
end note

note bottom of ReportingClient
Agregge les donnees
de tous les microservices
via API REST
end note

@enduml
```

**Infrastructure Layer**
- **Kong Gateway** : API Gateway avec load balancing
- **PostgreSQL Cluster** : 4 bases dédiées (inventory, ecommerce, retail, reporting)
- **Monitoring Stack** : Prometheus (métriques) + Grafana (dashboards)

**Application Layer**
- **4 Microservices** : Services métier indépendants
- **FastAPI Framework** : APIs REST standardisées
- **SQLAlchemy ORM** : Mapping objet-relationnel
- **Pydantic Schemas** : Validation et sérialisation

**Domain Layer**
- **Entities** : Modèles métier par domaine
- **Services** : Logique métier encapsulée
- **Repositories** : Abstraction accès données

### 5.2 Vue Composants détaillée

#### Inventory API (Service le plus critique - 3 instances)
```
├── Products Service
│   ├── Product Entity
│   ├── Product Repository
│   └── Product Endpoints
├── Categories Service
│   ├── Category Entity
│   ├── Category Repository
│   └── Category Endpoints
├── Stock Service
│   ├── StockMovement Entity
│   ├── Stock Repository
│   └── Stock Management Endpoints
├── Alerts Service
│   ├── StockAlert Entity
│   └── Alert Logic
└── Infrastructure
    ├── FastAPI Application
    ├── SQLAlchemy Models
    ├── Prometheus Metrics
    └── PostgreSQL Connection
```

#### Ecommerce API
```
├── Customer Service
├── Cart Service
├── Order Service
├── Authentication Service
└── Infrastructure (FastAPI + SQLAlchemy + PostgreSQL)
```

#### Retail API
```
├── Store Service
├── CashRegister Service
├── Sale Service
└── Infrastructure (FastAPI + SQLAlchemy + PostgreSQL)
```

#### Reporting API
```
├── Report Service
├── Analytics Service
├── Data Aggregation Service
└── Infrastructure (FastAPI + SQLAlchemy + PostgreSQL)
```

### 5.3 Vue Logique - Modèle de Domaine

**Référence** : Vue Logique `docs/docs4+1/vue-logique.puml`

#### Diagramme Entités Métier par Domaine

```plantuml
@startuml vue-logique
!define RECTANGLE class

title Documentation 4+1 - Vue Logique

package "Inventory Domain" {
    RECTANGLE Product {
        +id: Integer
        +name: String
        +description: String
        +price: Decimal
        +category_id: Integer
        +is_active: Boolean
        +created_at: DateTime
        +updated_at: DateTime
        --
        +reduce_stock(quantity: Integer)
        +increase_stock(quantity: Integer)
        +calculate_total_value()
    }
    
    RECTANGLE Category {
        +id: Integer
        +name: String
        +description: String
        +is_active: Boolean
        +created_at: DateTime
        --
        +get_products()
        +get_active_products()
    }
    
    RECTANGLE StockMovement {
        +id: Integer
        +product_id: Integer
        +movement_type: String
        +quantity: Integer
        +reason: String
        +created_at: DateTime
        +reference_id: Integer
        --
        +calculate_new_stock()
        +validate_movement()
    }
    
    RECTANGLE StockAlert {
        +id: Integer
        +product_id: Integer
        +alert_type: String
        +threshold: Integer
        +current_stock: Integer
        +is_resolved: Boolean
        +created_at: DateTime
        --
        +check_conditions()
        +resolve_alert()
    }
}

package "Retail Domain" {
    RECTANGLE Store {
        +id: Integer
        +name: String
        +address: String
        +phone: String
        +email: String
        +manager_name: String
        +is_active: Boolean
        +created_at: DateTime
        --
        +get_cash_registers()
        +get_sales_summary()
        +calculate_performance()
    }
    
    RECTANGLE CashRegister {
        +id: Integer
        +store_id: Integer
        +register_number: String
        +is_active: Boolean
        +created_at: DateTime
        --
        +process_sale()
        +get_daily_sales()
    }
    
    RECTANGLE Sale {
        +id: Integer
        +store_id: Integer
        +cash_register_id: Integer
        +total_amount: Decimal
        +status: String
        +created_at: DateTime
        +updated_at: DateTime
        --
        +add_line_item()
        +calculate_total()
        +finalize_sale()
    }
    
    RECTANGLE SaleLine {
        +id: Integer
        +sale_id: Integer
        +product_id: Integer
        +quantity: Integer
        +unit_price: Decimal
        +total_price: Decimal
        --
        +calculate_line_total()
        +validate_stock()
    }
}

package "Ecommerce Domain" {
    RECTANGLE Customer {
        +id: Integer
        +first_name: String
        +last_name: String
        +email: String
        +phone: String
        +password_hash: String
        +is_active: Boolean
        +created_at: DateTime
        --
        +authenticate()
        +create_cart()
        +get_orders()
    }
    
    RECTANGLE Address {
        +id: Integer
        +customer_id: Integer
        +type: String
        +street: String
        +city: String
        +postal_code: String
        +country: String
        +is_default: Boolean
        --
        +validate_address()
        +format_full_address()
    }
    
    RECTANGLE Cart {
        +id: Integer
        +customer_id: Integer
        +session_id: String
        +status: String
        +created_at: DateTime
        +updated_at: DateTime
        --
        +add_item()
        +remove_item()
        +calculate_total()
        +checkout()
    }
    
    RECTANGLE Order {
        +id: Integer
        +customer_id: Integer
        +order_number: String
        +status: String
        +total_amount: Decimal
        +shipping_address_id: Integer
        +billing_address_id: Integer
        +created_at: DateTime
        --
        +process_payment()
        +update_status()
        +calculate_total()
    }
}

package "Reporting Domain" {
    RECTANGLE Report {
        +id: Integer
        +report_type: String
        +title: String
        +description: String
        +generated_at: DateTime
        +parameters: JSON
        +data: JSON
        +status: String
        --
        +generate_report()
        +export_to_pdf()
        +schedule_generation()
    }
    
    RECTANGLE Analytics {
        +id: Integer
        +metric_name: String
        +metric_value: Decimal
        +period_start: DateTime
        +period_end: DateTime
        +category: String
        +created_at: DateTime
        --
        +calculate_metrics()
        +compare_periods()
    }
}

' Relations intra-domaine
Product ||--o{ Category : belongs_to
Product ||--o{ StockMovement : has_many
Product ||--o{ StockAlert : has_many

Store ||--o{ CashRegister : has_many
Store ||--o{ Sale : has_many
Sale ||--o{ SaleLine : has_many

Customer ||--o{ Address : has_many
Customer ||--o{ Cart : has_many
Customer ||--o{ Order : has_many

Report ||--o{ Analytics : contains

' Relations inter-domaines (API calls)
SaleLine ..> Product : "calls via API"
Order ..> Product : "calls via API"
Report ..> Order : "aggregates via API"
Report ..> Sale : "aggregates via API"
Report ..> Product : "aggregates via API"

@enduml
```

---

## 6. Vue d'Exécution

### 6.1 Scénarios Principaux

**Référence** : Vue Processus `docs/docs4+1/vue-processus.puml`

#### Scénario 1 : Commande E-commerce
```
Client → Kong Gateway → Ecommerce API : POST /orders
Ecommerce API → Kong Gateway → Inventory API : GET /products/{id}
Inventory API → Kong Gateway → Ecommerce API : Product details
Ecommerce API → Kong Gateway → Inventory API : POST /products/{id}/reduce-stock
Inventory API → Ecommerce Database : Update stock
Ecommerce API → Ecommerce Database : Create order
Ecommerce API → Kong Gateway → Client : Order confirmation
```

#### Scénario 2 : Vente en Magasin
```
Employé → Kong Gateway → Retail API : POST /sales
Retail API → Kong Gateway → Inventory API : GET /products/{id}
Inventory API → Kong Gateway → Retail API : Product details
Retail API → Kong Gateway → Inventory API : POST /products/{id}/reduce-stock
Inventory API → Inventory Database : Update stock
Retail API → Retail Database : Create sale
Retail API → Kong Gateway → Employé : Sale confirmation
```

### 6.2 Cas d'Utilisation Métier

**Référence** : Vue Scénarios `docs/docs4+1/scenarios.puml`

**3 Acteurs principaux :**
- **Client Web** : Commandes e-commerce, consultation catalogue
- **Employé Magasin** : Ventes, gestion stock local
- **Administrateur** : Configuration, monitoring, rapports

**4 Domaines métier :**
- **E-commerce** : Gestion commandes clients
- **Inventaire** : Gestion produits et stocks
- **Retail** : Opérations magasins
- **Reporting** : Analyses et rapports

---

## 7. Vue de Déploiement

### 7.1 Architecture de Déploiement

**Référence** : Vue Physique `docs/docs4+1/vue-physique.puml`

**Infrastructure Docker Compose**
```yaml
# Kong Gateway (Port 8000)
kong-gateway:
  image: kong:latest
  ports: ["8000:8000"]

# Inventory API (3 instances load-balancées)
inventory-api-1:
  build: ./services/inventory-api
  ports: ["8001:8001"]
inventory-api-2:
  build: ./services/inventory-api
  ports: ["8001:8001"]
inventory-api-3:
  build: ./services/inventory-api
  ports: ["8001:8001"]

# Autres microservices
ecommerce-api:
  build: ./services/ecommerce-api
  ports: ["8000:8000"]
retail-api:
  build: ./services/retail-api
  ports: ["8002:8002"]
reporting-api:
  build: ./services/reporting-api
  ports: ["8003:8003"]

# Bases de données dédiées
inventory-db:
  image: postgres:15
  ports: ["5433:5432"]
ecommerce-db:
  image: postgres:15
  ports: ["5450:5432"]
retail-db:
  image: postgres:15
  ports: ["5434:5432"]
reporting-db:
  image: postgres:15
  ports: ["5435:5432"]

# Monitoring
prometheus:
  image: prom/prometheus
  ports: ["9090:9090"]
grafana:
  image: grafana/grafana
  ports: ["3000:3000"]
```

### 7.2 Configuration Kong Gateway

**Référence** : `kong/kong-loadbalanced.yml`

```yaml
# Service Inventory avec Load Balancing
services:
  - name: inventory-service
    url: http://inventory-api-1:8001
    plugins:
      - name: prometheus
      - name: cors
# Routes et load balancing sur 3 instances
routes:
  - name: inventory-route
    service: inventory-service
    paths: ["/api/v1/inventory"]
```

---

## 8. Concepts Transversaux

### 8.1 Sécurité et Authentification

#### 8.1.1 Gestion des Clés API via Kong Gateway

**Architecture centralisée :** Kong Gateway gère l'authentification par clés API pour tous les microservices.

**Consommateurs et clés API définis :**
```yaml
consumers:
  - username: admin-user
    keyauth_credentials:
      - key: admin-api-key-12345
  - username: frontend-app  
    keyauth_credentials:
      - key: frontend-api-key-67890
  - username: mobile-app
    keyauth_credentials:
      - key: mobile-api-key-abcde
  - username: external-partner
    keyauth_credentials:
      - key: partner-api-key-fghij
```

**Plugin key-auth activé :** Sur tous les services via configuration Kong déclarative.

**Rate limiting par consommateur :**
- **Admin** : 1000 requêtes/heure
- **Frontend** : 2000 requêtes/heure  
- **Mobile** : 1000 requêtes/heure
- **Partner** : 500 requêtes/heure

**Utilisation :**
```bash
curl -H "apikey: admin-api-key-12345" \
     http://localhost:9000/inventory/api/v1/products/
```

#### 8.1.2 Autres Aspects Sécurité

**JWT Tokens :** Gérés par Ecommerce API pour l'authentification client
**Autorisation :** Contrôle d'accès par rôle utilisateur
**Communication :** HTTPS obligatoire en production
**Données sensibles :** Chiffrement bcrypt pour mots de passe
**CORS :** Configuration Kong pour accès cross-origin

### 8.2 Logging Centralisé et Traçabilité

#### 8.2.1 Architecture du Logging

**Approche multi-niveaux :** Logging centralisé via Kong Gateway + logging structuré par microservice.

**Composants du système de logging :**

1. **Kong Gateway - Logging Centralisé**
```yaml
# Plugin file-log activé sur tous les services
plugins:
  - name: file-log
    config:
      path: /var/log/kong/inventory-api.log
  - name: request-transformer
    config:
      add.headers: 
        - X-Service-Name:inventory-api
        - X-Gateway:kong
```

2. **Microservices - Logging Structuré**
```python
# Configuration de logging avancée par service
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

# Middleware de logging avec Request-ID
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"🔍 [{INSTANCE_ID}][{request_id}] {request.method} {request.url} - Started")
    # ... traitement et logging de la réponse
```

#### 8.2.2 Traçabilité des Requêtes

**Request-ID unique :** Généré par chaque microservice et propagé dans les headers.
```
X-Request-ID: a1b2c3d4
X-Instance-ID: inventory-api-1
X-Service-Name: inventory-api
X-Gateway: kong
```

**Corrélation des logs :** Suivi des requêtes à travers tous les services via Request-ID.

**Exemple de flux de logs :**
```
Kong:      [a1b2c3d4] POST /inventory/api/v1/products → inventory-api
Inventory: [inventory-api-1][a1b2c3d4] POST /api/v1/products - Started
Inventory: [inventory-api-1][a1b2c3d4] 201 - Completed in 45ms
Kong:      [a1b2c3d4] POST /inventory/api/v1/products ← 201 (47ms)
```

#### 8.2.3 Types de Logs

**Référence :** Configuration détaillée dans `src/api/logging_config.py`

1. **API Logs** : Requêtes HTTP avec métriques de performance
2. **Business Logs** : Opérations métier en format JSON structuré  
3. **Error Logs** : Erreurs avec contexte complet et stack traces
4. **Access Logs** : Logs d'accès Kong avec authentification

**Rotation et archivage :**
- Taille maximale : 10MB par fichier
- Rétention : 5-10 fichiers de sauvegarde
- Nommage : `{service}_{type}_YYYY-MM-DD.log`

#### 8.2.4 Centralisation et Observabilité

**Kong Gateway :** Point central de collecte des logs d'accès.
**Prometheus :** Métriques extraites des logs pour alertes.
**Grafana :** Dashboards basés sur les métriques de logging.

### 8.3 Performance et Scalabilité

**Load Balancing :** 3 instances Inventory API via Kong
**Optimisations :**
- Connection pooling par microservice
- Requêtes optimisées par domaine
- Métriques de performance Prometheus

**Cibles de performance :**
- 100+ utilisateurs simultanés
- Latence p95 < 105ms
- Taux d'erreur < 1%

### 8.4 Observabilité

**Métriques :** Prometheus avec collectors par microservice
**Dashboards :** Grafana avec vues par service et globales
**Alertes :** Règles automatiques sur latence et erreurs
**Logs :** Logging structuré par microservice (voir section 8.2)
**Health checks :** Endpoints `/health` sur chaque service

### 8.5 Gestion des Erreurs

**Circuit Breaker :** Protection contre pannes en cascade
**Retry Logic :** Tentatives automatiques avec backoff
**Graceful Degradation :** Réponses partielles en cas d'erreur
**Timeout Configuration :** Délais maximum par service

```python
# Pattern appliqué dans chaque microservice
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

---

## 9. Décisions

### 9.1 Architectural Decision Records (ADR)

#### ADR-005 : Kong Gateway pour Load Balancing
**Status** : Accepted  
**Context** : Besoin d'un point d'entrée unique avec load balancing pour les 3 instances Inventory API  
**Decision** : Adopter Kong Gateway comme solution intégrée API Gateway + Load Balancer  
**Alternatives considérées** :
- Nginx + Kong séparés
- HAProxy + Kong
- Service Mesh (Istio)
- AWS Application Load Balancer

**Consequences** :
- **Positives** : Simplicité opérationnelle, monitoring intégré, plugins Kong
- **Négatives** : Single point of failure, courbe d'apprentissage Kong
- **Métriques** : 100 utilisateurs simultanés, latence p95 < 105ms, taux d'erreur < 1%

#### ADR-006 : Bases de Données Dédiées par Microservice
**Status** : Accepted  
**Context** : Isolation des données et autonomie des microservices  
**Decision** : Pattern "Database per Service" avec PostgreSQL dédiées  
**Alternatives considérées** :
- Base de données partagée
- Event Sourcing avec EventStore
- Vues matérialisées dédiées
- Microservices avec bases NoSQL

**Consequences** :
- **Positives** : Isolation complète, autonomie des équipes, scalabilité indépendante
- **Négatives** : Complexité transactions distribuées, duplication données
- **Implémentation** : Communication uniquement via API REST, pas de requêtes SQL cross-service

#### ADR-007 : Logging Centralisé et Clés API via Kong Gateway
**Status** : Accepted  
**Context** : Besoin de traçabilité complète et d'authentification centralisée pour l'architecture microservices  
**Decision** : 
- Logging centralisé via Kong Gateway avec plugin file-log
- Authentification par clés API gérée centralement par Kong
- Request-ID unique pour traçage inter-services
- Headers de traçabilité ajoutés automatiquement par Kong

**Alternatives considérées** :
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd + Centralized logging
- Authentification JWT distribuée
- Service-to-service mTLS

**Consequences** :
- **Positives** : Traçabilité complète des requêtes, authentification centralisée, simplification des microservices
- **Négatives** : Kong devient point de collecte critique, gestion des logs en local
- **Implémentation** : Plugin file-log Kong + middleware logging FastAPI avec Request-ID

### 9.2 Alternatives Écartées

**Service Mesh :** Complexité excessive pour 4 microservices
**Event-Driven Architecture :** Pas de messaging complexe requis
**NoSQL :** Besoin de cohérence transactionnelle forte
**Kubernetes :** Infrastructure trop complexe pour l'équipe

---

## 10. Scénarios de Qualité

### 10.1 Performance

**Scenario P1 : Charge Normale**
- **Source** : 100 utilisateurs simultanés
- **Stimulus** : Requêtes GET /products
- **Environment** : 3 instances Inventory API
- **Response** : Répartition équitable des requêtes
- **Measure** : Latence p95 < 105ms, taux d'erreur < 1%

**Architecture Response** :
- Load balancing Kong avec algorithme round-robin
- Métriques Prometheus par instance
- Alertes automatiques si seuils dépassés

### 10.2 Disponibilité

**Scenario A1 : Panne d'une instance**
- **Source** : Instance Inventory API crash
- **Stimulus** : Perte de 33% capacité
- **Environment** : Kong Gateway actif
- **Response** : Redirection automatique vers instances saines
- **Measure** : Temps de récupération < 30 secondes

**Architecture Response** :
- Health checks Kong toutes les 10 secondes
- Retrait automatique des instances défaillantes
- Monitoring Grafana avec alertes

### 10.3 Modifiabilité

**Scenario M1 : Nouveau microservice**
- **Source** : Équipe développement
- **Stimulus** : Ajout Payment API
- **Environment** : Architecture existante
- **Response** : Intégration sans impact sur services existants
- **Measure** : 1 jour de développement

**Architecture Response** :
- Configuration Kong déclarative
- Base de données dédiée
- Monitoring automatique

---

## 11. Risques et Dette Technique

### 11.1 Risques Techniques Identifiés

#### RISK-001 : Kong Single Point of Failure
**Probabilité :** Moyenne  
**Impact :** Élevé  
**Mitigation :**
- Health checks et monitoring continu
- Plan de basculement d'urgence
- Documentation procédures de récupération

#### RISK-002 : Cohérence des Données Inter-Services
**Probabilité :** Moyenne  
**Impact :** Moyen  
**Mitigation :**
- Validation en temps réel des stocks
- Mécanismes de compensation en cas d'erreur
- Monitoring des transactions distribuées

#### RISK-003 : Performance Dégradée (Latence Réseau)
**Probabilité :** Faible  
**Impact :** Moyen  
**Mitigation :**
- Optimisation des requêtes inter-services
- Métriques de latence détaillées
- Alertes proactives

### 11.2 Dette Technique

#### DEBT-001 : Absence de Circuit Breaker
**Urgence** : Moyenne  
**Effort** : 5 jours  
**Description** : Pas de protection contre les pannes en cascade
**Impact** : Risque d'indisponibilité globale


#### DEBT-002 : Monitoring Basique
**Urgence** : Faible  
**Effort** : 1 semaine  
**Description** : Pas de tracing distribué
**Impact** : Difficultés de debugging inter-services

---

## 12. Glossaire

### Termes Techniques

**API Gateway** : Point d'entrée unique pour toutes les requêtes client  
**Load Balancing** : Répartition des requêtes entre plusieurs instances  
**Microservice** : Service indépendant avec base de données dédiée  
**Observabilité** : Capacité à comprendre l'état interne du système  
**Circuit Breaker** : Pattern de protection contre les pannes en cascade  
**Health Check** : Vérification automatique de l'état d'un service  
**Request-ID** : Identifiant unique pour tracer une requête à travers tous les services  
**Kong Consumer** : Entité Kong représentant un utilisateur ou application avec clés API  
**File-log Plugin** : Plugin Kong pour logging centralisé dans des fichiers  
**Key-auth Plugin** : Plugin Kong pour authentification par clés API  

### Termes Métier

**Bounded Context** : Frontière claire d'un domaine métier  
**Database per Service** : Pattern où chaque microservice a sa propre base  
**Saga Pattern** : Gestion des transactions distribuées  
**Stock Movement** : Mouvement de stock (entrée/sortie)  
**Cross-Origin** : Accès depuis un domaine différent (CORS)  

### Métriques et KPIs

**Latence p95** : 95% des requêtes sous un seuil de temps  
**Taux d'erreur** : Pourcentage de requêtes en erreur  
**Throughput** : Nombre de requêtes par seconde  
**Uptime** : Pourcentage de temps de fonctionnement  
**MTTR** : Mean Time To Recovery (temps moyen de récupération)  

---

**Fin du rapport Arc42**  
*Document de référence pour l'architecture microservices - Labs 3 à 5* 