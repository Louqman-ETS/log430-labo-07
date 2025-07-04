# 🛍️ Ecommerce API

Service unifié de gestion des clients, paniers et commandes pour une plateforme e-commerce.

## 🏗️ Architecture

Cette API fusionne trois domaines métier principaux :

- **Customers** : Gestion des clients, authentification et adresses
- **Carts** : Gestion des paniers d'achat
- **Orders** : Gestion des commandes et processus de checkout

## 🚀 Fonctionnalités

### Customers
- ✅ Inscription et connexion des clients
- ✅ Gestion des profils clients
- ✅ Gestion des adresses (livraison/facturation)
- ✅ Authentification JWT
- ✅ Changement de mot de passe

### Carts
- ✅ Création et gestion des paniers
- ✅ Ajout/suppression d'articles
- ✅ Validation des paniers (stock, prix)
- ✅ Paniers pour clients connectés et invités
- ✅ Statistiques des paniers

### Orders
- ✅ Processus de checkout complet
- ✅ Gestion des statuts de commande
- ✅ Suivi des commandes
- ✅ Gestion des paiements
- ✅ Statistiques des commandes

## 📋 Prérequis

- Python 3.11+
- PostgreSQL
- Docker (optionnel)

## 🛠️ Installation

### Avec Docker

```bash
# Construire l'image
docker build -t ecommerce-api .

# Lancer le conteneur
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:port/db \
  -e SECRET_KEY=your-secret-key \
  ecommerce-api
```

### Installation locale

```bash
# Cloner le projet
cd services/ecommerce-api

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export DATABASE_URL="postgresql://user:password@host:port/db"
export SECRET_KEY="your-secret-key"

# Lancer l'API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@localhost/ecommerce` |
| `SECRET_KEY` | Clé secrète pour JWT | `your-secret-key-here` |
| `PRODUCTS_API_URL` | URL de l'API Products | `http://products-api:8001` |
| `STOCK_API_URL` | URL de l'API Stock | `http://stock-api:8004` |

## 📚 API Documentation

Une fois l'API lancée, la documentation est disponible à :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔌 Endpoints principaux

### Customers
```
POST   /api/v1/customers/register     # Inscription
POST   /api/v1/customers/login        # Connexion
GET    /api/v1/customers/             # Liste des clients
GET    /api/v1/customers/{id}         # Détails d'un client
PUT    /api/v1/customers/{id}         # Mise à jour client
DELETE /api/v1/customers/{id}         # Suppression client
```

### Carts
```
GET    /api/v1/carts/                 # Liste des paniers
POST   /api/v1/carts/                 # Créer un panier
GET    /api/v1/carts/{id}             # Détails d'un panier
POST   /api/v1/carts/{id}/items       # Ajouter un article
PUT    /api/v1/carts/{id}/items/{item_id}  # Modifier un article
DELETE /api/v1/carts/{id}/items/{item_id}  # Supprimer un article
```

### Orders
```
GET    /api/v1/orders/                # Liste des commandes
POST   /api/v1/orders/checkout        # Créer une commande
GET    /api/v1/orders/{id}            # Détails d'une commande
PUT    /api/v1/orders/{id}/status     # Mettre à jour le statut
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Lancer les tests avec couverture
pytest --cov=src

# Lancer les tests en mode verbose
pytest -v
```

## 📊 Base de données

### Tables principales

- `customers` : Clients
- `customer_auth` : Authentification des clients
- `addresses` : Adresses des clients
- `carts` : Paniers
- `cart_items` : Articles dans les paniers
- `orders` : Commandes
- `order_items` : Articles dans les commandes

### Relations

- Un client peut avoir plusieurs adresses
- Un client peut avoir plusieurs paniers
- Un client peut avoir plusieurs commandes
- Un panier peut contenir plusieurs articles
- Une commande peut contenir plusieurs articles

## 🔒 Sécurité

- Authentification JWT
- Hachage des mots de passe avec bcrypt
- Validation des données avec Pydantic
- Gestion des erreurs standardisée
- Logging structuré

## 📈 Monitoring

- Endpoint de santé : `GET /health`
- Logging structuré avec Request-ID
- Métriques de performance
- Gestion d'erreurs centralisée

## 🤝 Intégration

L'API communique avec d'autres services :

- **Products API** : Récupération des informations produits
- **Stock API** : Vérification de la disponibilité

## 🚀 Déploiement

### Docker Compose

```yaml
version: '3.8'
services:
  ecommerce-api:
    build: ./services/ecommerce-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ecommerce
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
```

## 📝 Notes de développement

- Architecture DDD (Domain-Driven Design)
- Séparation claire des couches (API, Services, Modèles)
- Code modulaire et réutilisable
- Documentation complète
- Tests automatisés

## 🔄 Migration depuis les micro-services

Cette API remplace les services suivants :
- `cart-api`
- `customers-api` 
- `orders-api`

Tous les endpoints sont conservés avec les mêmes interfaces pour assurer la compatibilité. 