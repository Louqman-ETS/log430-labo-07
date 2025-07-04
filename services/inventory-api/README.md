# Inventory API

API RESTful unifiée pour la gestion des produits, catégories et stocks selon les principes Domain-Driven Design (DDD).

## 🎯 Fonctionnalités

### Gestion des Produits
- ✅ CRUD complet des produits
- ✅ Recherche et filtrage
- ✅ Pagination
- ✅ Gestion des catégories
- ✅ Statut actif/inactif

### Gestion des Stocks
- ✅ Suivi des mouvements de stock (entrées, sorties, ajustements)
- ✅ Alertes automatiques (stock faible, rupture, surstock)
- ✅ Historique des mouvements
- ✅ Ajustements manuels
- ✅ Réduction/augmentation de stock

### Fonctionnalités Avancées
- ✅ Logging structuré avec Request-ID
- ✅ Gestion d'erreurs standardisée
- ✅ Documentation OpenAPI/Swagger
- ✅ Architecture DDD
- ✅ Base de données PostgreSQL

## 🏗️ Architecture

```
inventory-api/
├── src/
│   ├── api/v1/
│   │   ├── products.py      # Endpoints produits
│   │   ├── categories.py    # Endpoints catégories
│   │   ├── stock.py         # Endpoints stock
│   │   └── router.py        # Router principal
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   ├── services.py          # Services métier
│   ├── database.py          # Configuration DB
│   ├── init_db.py           # Initialisation DB
│   └── main.py              # Application FastAPI
├── tests/                   # Tests unitaires
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Configuration Docker
└── README.md               # Documentation
```

## 🚀 Installation et Démarrage

### Avec Docker
```bash
# Construire l'image
docker build -t inventory-api .

# Démarrer le service
docker run -p 8001:8001 inventory-api
```

### En local
```bash
# Installer les dépendances
pip install -r requirements.txt

# Démarrer l'API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

## 📋 Endpoints

### Produits
```
GET    /api/v1/products/              - Liste des produits
POST   /api/v1/products/              - Créer un produit
GET    /api/v1/products/{id}          - Détails d'un produit
PUT    /api/v1/products/{id}          - Modifier un produit
DELETE /api/v1/products/{id}          - Supprimer un produit

# Gestion du stock
GET    /api/v1/products/{id}/stock    - Info stock d'un produit
PUT    /api/v1/products/{id}/stock/adjust - Ajuster le stock
GET    /api/v1/products/{id}/stock/status - Statut complet du stock
```

### Catégories
```
GET    /api/v1/categories/            - Liste des catégories
POST   /api/v1/categories/            - Créer une catégorie
GET    /api/v1/categories/{id}        - Détails d'une catégorie
PUT    /api/v1/categories/{id}        - Modifier une catégorie
DELETE /api/v1/categories/{id}        - Supprimer une catégorie
```

### Stock
```
# Mouvements de stock
GET    /api/v1/stock/movements        - Historique des mouvements
POST   /api/v1/stock/movements        - Créer un mouvement

# Alertes de stock
GET    /api/v1/stock/alerts           - Alertes actives
PUT    /api/v1/stock/alerts/{id}      - Marquer une alerte comme résolue

# Gestion du stock
GET    /api/v1/stock/summary          - Résumé de l'inventaire
PUT    /api/v1/stock/products/{id}/stock/reduce   - Réduire le stock
PUT    /api/v1/stock/products/{id}/stock/increase - Augmenter le stock
GET    /api/v1/stock/products/{id}/stock          - Info stock
```

## 🔧 Configuration

### Variables d'environnement
```bash
DATABASE_URL=postgresql://postgres:password@inventory-db:5432/inventory_db
```

### Base de données
L'API utilise PostgreSQL avec les tables suivantes :
- `categories` - Catégories de produits
- `products` - Produits avec stock intégré
- `stock_movements` - Historique des mouvements
- `stock_alerts` - Alertes de stock

## 📊 Données de Test

L'API inclut des données de test automatiques :
- 6 catégories (Alimentaire, Électronique, Vêtements, etc.)
- 18 produits avec stocks variés
- Mouvements de stock simulés
- Alertes de stock automatiques

## 🧪 Tests

```bash
# Exécuter les tests
python -m pytest tests/ -v

# Tests avec couverture
python -m pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentation

- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc
- **Health Check** : http://localhost:8001/health

## 🔄 Migration depuis les APIs séparées

Cette API remplace les anciennes `products-api` et `stock-api` avec les améliorations suivantes :

### Avantages
- ✅ **Performance** : Moins de communication inter-services
- ✅ **Cohérence** : Base de données unifiée
- ✅ **Simplicité** : Une seule API à maintenir
- ✅ **DDD** : Domaine inventory cohérent
- ✅ **Fonctionnalités** : Alertes automatiques, historique complet

### Compatibilité
- ✅ Tous les endpoints existants sont préservés
- ✅ Logique métier identique
- ✅ Schémas de données compatibles
- ✅ Migration transparente

## 🚀 Déploiement

### Docker Compose
```yaml
inventory-api:
  build: ./inventory-api
  ports:
    - "8001:8001"
  environment:
    DATABASE_URL: postgresql://postgres:password@inventory-db:5432/inventory_db
  depends_on:
    - inventory-db
```

### Production
- Utiliser un reverse proxy (nginx)
- Configurer SSL/TLS
- Mettre en place la surveillance
- Configurer les sauvegardes de base de données 