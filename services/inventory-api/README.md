# Inventory API

Service unifié pour la gestion des produits et du stock.

## Fonctionnalités

### Gestion des Produits
- CRUD complet des produits
- Recherche et filtrage
- Pagination
- Gestion des catégories
- Statut actif/inactif

### Gestion du Stock
- Suivi des mouvements de stock (entrées, sorties, ajustements)
- Alertes automatiques (stock faible, rupture, surstock)
- Historique des mouvements
- Ajustements manuels
- Réduction/augmentation de stock

### Fonctionnalités Techniques
- Logging structuré avec Request-ID
- Gestion d'erreurs standardisée
- Documentation OpenAPI/Swagger
- Architecture DDD
- Base de données PostgreSQL

## Architecture

```
├── src/
│   ├── api/v1/
│   │   ├── products.py      # Endpoints produits
│   │   ├── categories.py    # Endpoints catégories
│   │   ├── stock.py         # Endpoints stock
│   │   └── router.py        # Routage principal
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   ├── services.py          # Logique métier
│   ├── database.py          # Configuration DB
│   └── main.py              # Point d'entrée FastAPI
├── tests/
│   ├── test_products.py     # Tests produits
│   ├── test_categories.py   # Tests catégories
│   ├── test_stock.py        # Tests stock
│   └── conftest.py          # Configuration tests
└── requirements.txt         # Dépendances
```

## Installation et Démarrage

### Prérequis
- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose

### Installation
```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
export DATABASE_URL="postgresql://user:password@localhost:5432/inventory"

# Initialisation de la base de données
python src/init_db.py

# Démarrage de l'API
python src/main.py
```

## Endpoints

### Produits
- `GET /api/v1/products/` - Liste des produits (avec pagination)
- `POST /api/v1/products/` - Créer un produit
- `GET /api/v1/products/{id}` - Détails d'un produit
- `PUT /api/v1/products/{id}` - Modifier un produit
- `DELETE /api/v1/products/{id}` - Supprimer un produit
- `GET /api/v1/products/search` - Rechercher des produits

### Catégories
- `GET /api/v1/categories/` - Liste des catégories
- `POST /api/v1/categories/` - Créer une catégorie
- `GET /api/v1/categories/{id}` - Détails d'une catégorie
- `PUT /api/v1/categories/{id}` - Modifier une catégorie
- `DELETE /api/v1/categories/{id}` - Supprimer une catégorie

### Stock
- `GET /api/v1/stock/` - État du stock
- `POST /api/v1/stock/movement` - Enregistrer un mouvement
- `GET /api/v1/stock/movements` - Historique des mouvements
- `GET /api/v1/stock/alerts` - Alertes de stock
- `POST /api/v1/stock/adjust` - Ajustement de stock
- `GET /api/v1/stock/stats` - Statistiques de stock

### Exemples d'utilisation
```bash
# Créer un produit
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Produit Test", "description": "Description", "price": 29.99, "category_id": 1}'

# Rechercher des produits
curl "http://localhost:8001/api/v1/products/search?q=test&category_id=1"

# Ajouter du stock
curl -X POST http://localhost:8001/api/v1/stock/movement \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 100, "movement_type": "IN", "reason": "Initial stock"}'
```

## Configuration

Variables d'environnement :
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/inventory
API_PORT=8001
DEBUG=false
LOG_LEVEL=INFO
```

## Tests

### Lancer les tests
```bash
python -m pytest tests/ -v
```

### Tests avec couverture
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Documentation

- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc
- **OpenAPI JSON** : http://localhost:8001/openapi.json

## Migration depuis les APIs séparées

Cette API unifie les fonctionnalités des anciennes APIs `products-api` et `stock-api`.

### Avantages
- **Performance** : Moins de communication inter-services
- **Cohérence** : Base de données unifiée
- **Simplicité** : Une seule API à maintenir
- **DDD** : Domaine inventory cohérent
- **Fonctionnalités** : Alertes automatiques, historique complet

### Compatibilité
- Tous les endpoints existants sont préservés
- Logique métier identique
- Schémas de données compatibles
- Migration transparente

## Déploiement

### Docker
```bash
docker build -t inventory-api .
docker run -d -p 8001:8001 inventory-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  inventory-api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/inventory
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=inventory
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
``` 