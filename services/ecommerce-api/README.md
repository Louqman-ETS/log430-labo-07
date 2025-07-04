# Ecommerce API

Service unifié pour la gestion des clients, paniers et commandes e-commerce.

## Architecture

Cette API unifie les fonctionnalités de gestion des clients, paniers et commandes dans un seul service cohérent, suivant les principes Domain-Driven Design (DDD).

### Domaines
- **Customers** : Gestion des clients et authentification
- **Carts** : Gestion des paniers d'achat
- **Orders** : Gestion des commandes et processus de checkout

## Fonctionnalités

### Customers (Clients)
- Inscription et connexion des clients
- Gestion des profils clients
- Gestion des adresses (livraison/facturation)
- Authentification JWT
- Changement de mot de passe

### Carts (Paniers)
- Création et gestion des paniers
- Ajout/suppression d'articles
- Validation des paniers (stock, prix)
- Paniers pour clients connectés et invités
- Statistiques des paniers

### Orders (Commandes)
- Processus de checkout complet
- Gestion des statuts de commande
- Suivi des commandes
- Gestion des paiements
- Statistiques des commandes

## Prérequis

- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose

## Installation

### Option 1: Docker (Recommandé)
```bash
# Construire l'image
docker build -t ecommerce-api .

# Lancer avec docker-compose
docker-compose up -d
```

### Option 2: Installation locale
```bash
# Installer les dépendances
pip install -r requirements.txt

# Variables d'environnement
export DATABASE_URL="postgresql://user:password@localhost:5432/ecommerce"
export JWT_SECRET_KEY="your-secret-key"
export INVENTORY_API_URL="http://localhost:8001"

# Initialiser la base de données
python src/init_db.py

# Lancer l'API
python src/main.py
```

## Configuration

Variables d'environnement :
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
JWT_SECRET_KEY=your-secret-key
INVENTORY_API_URL=http://localhost:8001
API_PORT=8000
DEBUG=false
```

## API Documentation

L'API est documentée avec OpenAPI/Swagger :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

### Endpoints principaux

#### Customers
- `POST /api/v1/customers/register` - Inscription
- `POST /api/v1/customers/login` - Connexion
- `GET /api/v1/customers/profile` - Profil client
- `PUT /api/v1/customers/profile` - Modifier profil
- `POST /api/v1/customers/addresses` - Ajouter adresse
- `GET /api/v1/customers/addresses` - Lister adresses

#### Carts
- `POST /api/v1/carts/` - Créer panier
- `GET /api/v1/carts/{cart_id}` - Détails panier
- `POST /api/v1/carts/{cart_id}/items` - Ajouter article
- `PUT /api/v1/carts/{cart_id}/items/{item_id}` - Modifier quantité
- `DELETE /api/v1/carts/{cart_id}/items/{item_id}` - Supprimer article
- `GET /api/v1/carts/stats` - Statistiques paniers

#### Orders
- `POST /api/v1/orders/` - Créer commande (checkout)
- `GET /api/v1/orders/{order_id}` - Détails commande
- `GET /api/v1/orders/` - Lister commandes client
- `PUT /api/v1/orders/{order_id}/status` - Changer statut
- `GET /api/v1/orders/stats` - Statistiques commandes

## Tests

### Lancer les tests
```bash
# Tests unitaires
python -m pytest tests/ -v

# Tests avec couverture
python -m pytest tests/ --cov=src --cov-report=html

# Tests d'intégration
python -m pytest tests/test_integration.py -v
```

### Tests manuels
```bash
# Inscription client
curl -X POST http://localhost:8000/api/v1/customers/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "first_name": "Test", "last_name": "User"}'

# Connexion
curl -X POST http://localhost:8000/api/v1/customers/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Créer panier
curl -X POST http://localhost:8000/api/v1/carts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## Sécurité

### Authentification
- JWT tokens avec expiration
- Refresh tokens pour sessions longues
- Validation des mots de passe (longueur, complexité)

### Autorisations
- Clients ne peuvent accéder qu'à leurs propres données
- Validation des permissions sur tous les endpoints
- Logging des actions sensibles

### Validation
- Validation stricte des données d'entrée
- Sanitisation des inputs
- Protection contre les injections SQL
- Rate limiting par IP

### Données sensibles
- Hachage des mots de passe (bcrypt)
- Chiffrement des données PII
- Logs sans données sensibles

## Déploiement

### Docker
```bash
# Production
docker build -t ecommerce-api:prod .
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET_KEY="..." \
  ecommerce-api:prod
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: ecommerce-api
        image: ecommerce-api:prod
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ecommerce-secrets
              key: database-url
```

## Migration depuis les micro-services

Cette API unifie les fonctionnalités précédemment réparties dans plusieurs micro-services :

### Avant (micro-services séparés)
- `customer-service` : Gestion des clients
- `cart-service` : Gestion des paniers  
- `order-service` : Gestion des commandes

### Après (service unifié)
- `ecommerce-api` : Toutes les fonctionnalités e-commerce

### Avantages
- **Performance** : Moins de communication inter-services
- **Cohérence** : Transactions ACID entre domaines
- **Simplicité** : Une seule API à maintenir
- **Sécurité** : Authentification centralisée

### Compatibilité
- Tous les endpoints existants sont préservés
- Schémas de données identiques
- Migration transparente pour les clients
- Pas de breaking changes 