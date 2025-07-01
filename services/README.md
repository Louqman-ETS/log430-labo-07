# Microservices Architecture

Cette architecture divise l'API monolithique en 3 microservices distincts avec communication inter-services par API REST.

## Architecture

### 1. Products API (Port 8001)
- **Base de données**: PostgreSQL sur port 5433
- **Responsabilités**: 
  - Gestion des produits et catégories
  - Stock des produits
  - Opérations sur les stocks (réduction, etc.)

### 2. Stores API (Port 8002)
- **Base de données**: PostgreSQL sur port 5434
- **Responsabilités**:
  - Gestion des magasins
  - Gestion des caisses enregistreuses
  - Informations de contact des magasins

### 3. Reporting API (Port 8003)
- **Base de données**: PostgreSQL sur port 5435
- **Responsabilités**:
  - Gestion des ventes et lignes de vente
  - Stocks par magasin et stocks centraux
  - Demandes de réapprovisionnement
  - Génération de rapports et analytics
  - **Communication avec les autres services** pour enrichir les données

## Communication inter-services

Le service Reporting communique avec les autres services via HTTP/REST :

- **Products API**: Pour obtenir les informations des produits et catégories
- **Stores API**: Pour obtenir les informations des magasins et caisses

**Principe important**: Aucune communication SQL directe entre bases de données. Toute communication se fait via les API REST.

## Démarrage des services

### Prérequis
- Docker et Docker Compose installés
- Ports 8001, 8002, 8003, 5433, 5434, 5435 disponibles

### Commandes

```bash
# Démarrer tous les services
cd services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (données)
docker-compose down -v
```

## Endpoints principaux

### Products API (http://localhost:8001)
- `GET /api/v1/products/` - Liste des produits avec pagination
- `GET /api/v1/products/{id}` - Détail d'un produit
- `POST /api/v1/products/` - Créer un produit
- `POST /api/v1/products/{id}/reduce-stock?quantity=X` - Réduire le stock
- `GET /api/v1/categories/` - Liste des catégories
- `GET /docs` - Documentation Swagger

### Stores API (http://localhost:8002)
- `GET /api/v1/stores/` - Liste des magasins avec pagination
- `GET /api/v1/stores/{id}` - Détail d'un magasin
- `POST /api/v1/stores/` - Créer un magasin
- `GET /api/v1/cash-registers/` - Liste des caisses
- `GET /api/v1/cash-registers/store/{store_id}` - Caisses d'un magasin
- `GET /docs` - Documentation Swagger

### Reporting API (http://localhost:8003)
- `GET /api/v1/reports/global-summary` - Résumé global
- `GET /api/v1/reports/store-performances` - Performance des magasins
- `GET /api/v1/reports/top-products` - Top produits
- `POST /api/v1/sales/` - Créer une vente
- `GET /api/v1/sales/store/{store_id}` - Ventes d'un magasin
- `GET /docs` - Documentation Swagger

## Initialisation des données

Chaque service initialise automatiquement sa base de données avec des données d'exemple au premier démarrage :

- **Products**: 4 catégories, 14 produits
- **Stores**: 5 magasins, 15 caisses (3 par magasin)
- **Reporting**: 50 ventes avec lignes, stocks, demandes de réapprovisionnement

## Données cohérentes

Les données sont cohérentes entre les services :
- Les IDs des magasins dans Reporting correspondent aux magasins dans Stores
- Les IDs des produits dans Reporting correspondent aux produits dans Products
- Les caisses sont numérotées de 1 à 15 (3 par magasin)

## Surveillance

Chaque service expose un endpoint de santé :
- `GET /health` retourne `{"status": "healthy", "service": "nom_service"}`

## Architecture technique

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Products API  │    │   Stores API    │    │  Reporting API  │
│   (Port 8001)   │    │   (Port 8002)   │    │   (Port 8003)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│  Products DB    │    │   Stores DB     │    │  Reporting DB   │
│  (Port 5433)    │    │  (Port 5434)    │    │  (Port 5435)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘

                    Communication inter-services
                           (HTTP/REST)
                    ┌────────────────────────┐
                    │                        │
                    ▼                        ▼
              Products API ◄─────── Reporting API
                                            │
                                            ▼
                              Stores API ◄──┘
```

## Avantages de cette architecture

1. **Séparation des responsabilités**: Chaque service a une responsabilité claire
2. **Scalabilité**: Chaque service peut être mis à l'échelle indépendamment
3. **Résilience**: La panne d'un service n'affecte pas les autres (partiellement)
4. **Déploiement indépendant**: Chaque service peut être déployé séparément
5. **Technologies différentes**: Possibilité d'utiliser différentes technologies par service
6. **Base de données dédiée**: Chaque service contrôle ses propres données

## Considérations

1. **Latence réseau**: Communication inter-services ajoute de la latence
2. **Gestion des erreurs**: Gérer les pannes de communication entre services
3. **Cohérence des données**: Plus complexe avec les données distribuées
4. **Debugging**: Plus complexe à déboguer car les données sont réparties
5. **Transactions distribuées**: Plus complexe à gérer 