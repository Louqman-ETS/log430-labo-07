# Retail API

API RESTful de gestion des magasins et ventes - Architecture DDD

## Description

Cette API fusionne les fonctionnalités de gestion des magasins et des ventes dans un seul service cohérent selon les principes du Domain-Driven Design (DDD).

## Fonctionnalités

### Gestion des Magasins
- CRUD complet pour les magasins
- Gestion des statuts actif/inactif
- Détails complets avec statistiques
- Performances par magasin

### Gestion des Caisses Enregistreuses
- CRUD complet pour les caisses
- Association aux magasins
- Gestion des statuts actif/inactif

### Gestion des Ventes
- CRUD complet pour les ventes
- Lignes de vente avec produits
- Calcul automatique des totaux
- Statuts de vente (en cours, terminée, annulée)
- Statistiques et rapports

## Endpoints

### Magasins
- `GET /api/v1/stores` - Liste des magasins
- `POST /api/v1/stores` - Créer un magasin
- `GET /api/v1/stores/{id}` - Détails d'un magasin
- `PUT /api/v1/stores/{id}` - Modifier un magasin
- `DELETE /api/v1/stores/{id}` - Supprimer un magasin
- `GET /api/v1/stores/{id}/details` - Détails complets
- `GET /api/v1/stores/{id}/performance` - Performances

### Caisses Enregistreuses
- `GET /api/v1/cash-registers` - Liste des caisses
- `POST /api/v1/cash-registers` - Créer une caisse
- `GET /api/v1/cash-registers/{id}` - Détails d'une caisse
- `PUT /api/v1/cash-registers/{id}` - Modifier une caisse
- `DELETE /api/v1/cash-registers/{id}` - Supprimer une caisse

### Ventes
- `GET /api/v1/sales` - Liste des ventes (avec pagination)
- `POST /api/v1/sales` - Créer une vente
- `GET /api/v1/sales/{id}` - Détails d'une vente
- `PUT /api/v1/sales/{id}` - Modifier une vente
- `DELETE /api/v1/sales/{id}` - Annuler une vente
- `GET /api/v1/sales/stats/summary` - Résumé des statistiques
- `GET /api/v1/sales/stats/by-store` - Ventes par magasin
- `GET /api/v1/sales/stats/by-date` - Ventes par date

## Architecture

### Modèles de Données
- **Store** : Magasins avec informations de contact
- **CashRegister** : Caisses enregistreuses par magasin
- **Sale** : Transactions de vente
- **SaleLine** : Lignes de détail des ventes
- **StoreMetrics** : Métriques de performance

### Services
- **StoreService** : Logique métier pour les magasins
- **CashRegisterService** : Logique métier pour les caisses
- **SaleService** : Logique métier pour les ventes

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL
- Docker (optionnel)

### Variables d'Environnement
```bash
DATABASE_URL=postgresql://postgres:password@retail-db:5432/retail_db
```

### Installation Locale
```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker
```bash
docker build -t retail-api .
docker run -p 8002:8002 retail-api
```

## Documentation

- **Swagger UI** : http://localhost:8002/docs
- **ReDoc** : http://localhost:8002/redoc
- **Health Check** : http://localhost:8002/health

## Migration depuis les APIs séparées

Cette API remplace les anciennes APIs `sales-api` et `stores-api` avec les améliorations suivantes :

### Avantages de la Fusion
- **Cohérence** : Un seul service pour le domaine retail
- **Performance** : Moins d'appels inter-services
- **Simplicité** : Architecture plus simple à maintenir
- **Relations** : Gestion native des relations entre entités

### Endpoints Migrés
- `/api/v1/stores/*` (depuis stores-api)
- `/api/v1/sales/*` (depuis sales-api)
- Nouveaux endpoints pour les caisses enregistreuses

### Données d'Exemple
L'API inclut des données d'exemple pour :
- 5 magasins dans différentes régions
- 3 caisses enregistreuses par magasin
- 9 ventes d'exemple avec lignes de détail 