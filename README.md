# Système Multi-Magasins - LOG430

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)

Application web Flask pour la gestion de points de vente multi-magasins, API RESTful pour application externe, système de logging et déploiement Docker containerisé.

## Table des Matières

- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Architecture](#architecture)
- [Logging et Monitoring](#logging-et-monitoring)
- [API RESTful](#api-restful)
- [Déploiement Docker](#déploiement-docker)
- [Structure du Projet](#structure-du-projet)
- [Installation et Configuration](#installation-et-configuration)
- [Tests](#tests)
- [Utilisation](#utilisation)
- [Technologies Utilisées](#technologies-utilisées)

## Fonctionnalités Principales

### Interface Web (Flask)
- **Dashboard multi-magasins** : Vue d'ensemble de 5 magasins avec navigation intuitive
- **Rapports stratégiques** : KPIs globaux, performance par magasin, top produits, tendances
- **Point de vente complet** : Recherche produits, gestion panier, reçus, retours
- **Gestion stocks** : Stocks par magasin, alertes automatiques, réapprovisionnement
- **Interface responsive** : Bootstrap, design moderne et adaptatif

### API RESTful (FastAPI)
- **Architecture DDD** : Domain-Driven Design avec 3 domaines métier
- **Documentation automatique** : Swagger UI et ReDoc intégrés
- **Authentification** : Système de tokens sécurisé
- **Validation** : Pydantic pour la validation des données
- **Performance** : Optimisations asynchrones et mise en cache

### Système de Logging
- **Logging multi-niveaux** : API, Business, Erreurs
- **Rotation automatique** : Gestion intelligente des fichiers de logs
- **Formats multiples** : JSON structuré et texte lisible
- **Monitoring** : Métriques de performance et suivi des erreurs

## Architecture

### Architecture Multi-Applications Containerisée

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE MULTI-APPLICATIONS                n │
├─────────────────┬─────────────────┬─────────────────┬───────────────┤
│   PRESENTATION  │   APPLICATION   │   API SÉPARÉE   │    DONNÉES    │
│    (Frontend)   │   (Backend)     │  (Indépendante) │  (Database)   │
│                 │                 │                 │               │
│ • Navigateur    │ • Flask Web     │ • FastAPI       │ • PostgreSQL  │
│ • Templates     │ • Controllers   │ • DDD Domains   │ • External DB │
│ • Bootstrap     │ • Models        │ • Repositories  │ • Persistent  │
│ • JavaScript    │ • Services      │ • Services      │ • Volume      │
│                 │                 │ • Schemas       │               │
└─────────────────┴─────────────────┴─────────────────┴───────────────┘
         ↑                   ↑               ↑               ↑
    HTTP/HTTPS          Docker:8080    Docker:8000     External:5432
     Port 8080           Container      Container         Server
```

### Composants Principaux

#### 1. Application Web (Flask) - Port 8080
- **MVC Pattern** : Séparation claire des responsabilités
- **7 Contrôleurs** : Gestion modulaire des fonctionnalités
- **Templates Jinja2** : Interface utilisateur dynamique
- **Bootstrap 5** : Design responsive et moderne
- **Application indépendante** : Fonctionne de manière autonome

#### 2. API RESTful (FastAPI) - Port 8000
- **Domain-Driven Design** : Architecture en domaines métier
- **3 Domaines** : Products, Stores, Reporting
- **Repositories Pattern** : Abstraction de la couche de données
- **Services Layer** : Logique métier centralisée
- **Application séparée** : API indépendante de l'interface web

#### 3. Base de Données (PostgreSQL) - Port 5432
- **Connexions poolées** : Optimisation des performances
- **Partagée** : Utilisée par les deux applications
- **Migrations** : Gestion des schémas de données

### Caractéristiques de l'Architecture

- **Applications indépendantes** : Flask et FastAPI sont des applications séparées
- **Déploiement containerisé** : Chaque application dans son propre container
- **Base de données partagée** : Les deux applications accèdent à la même base PostgreSQL
- **Ports distincts** : Chaque application expose ses services sur des ports différents
- **Développement parallèle** : Les équipes peuvent travailler indépendamment sur chaque application

## Logging et Monitoring

### Architecture du Logging

Le système de logging est conçu pour fournir une visibilité complète sur le fonctionnement de l'application avec une séparation claire des types de logs.

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTÈME DE LOGGING                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   API LOGS      │  BUSINESS LOGS  │     ERROR LOGS          │
│                 │                 │                         │
│ • Requêtes HTTP │ • Opérations    │ • Exceptions            │
│ • Réponses      │   métier        │ • Stack traces          │
│ • Temps de      │ • Transactions  │ • Contexte d'erreur     │
│   réponse       │ • Validations   │ • Alertes critiques     │
│ • Headers       │ • Résultats     │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
         ↓               ↓                       ↓
   api_YYYY-MM-DD.log  business_YYYY-MM-DD.log  errors_YYYY-MM-DD.log
```

### Configuration des Logs

#### Types de Logs
- **API Logs** : Toutes les requêtes HTTP avec métriques de performance
- **Business Logs** : Opérations métier en format JSON structuré
- **Error Logs** : Erreurs avec contexte complet et stack traces

#### Rotation et Archivage
- **Taille maximale** : 10MB par fichier
- **Rétention** : 5-10 fichiers de sauvegarde
- **Nommage** : `{type}_YYYY-MM-DD.log`
- **Formats** : JSON pour le business, texte pour les API

#### Fonctionnalités Avancées
```python
# Logging automatique des requêtes HTTP
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Logging avec métriques de performance
    
# Logging des opérations métier
log_business_operation(
    operation="create_store",
    entity_type="Store",
    entity_id=store.id,
    user_id=current_user.id,
    details={"name": store.name, "location": store.location}
)

# Logging des erreurs avec contexte
log_error_with_context(
    error=exception,
    context={
        "endpoint": "/api/v1/stores",
        "method": "POST",
        "user_id": user_id,
        "request_data": request_data
    }
)
```

## API RESTful

### Architecture DDD (Domain-Driven Design)

L'API est structurée selon les principes du Domain-Driven Design avec une séparation claire des responsabilités.

```
┌─────────────────────────────────────────────────────────────┐
│                     API ARCHITECTURE                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   ENDPOINTS     │    DOMAINS      │      INFRASTRUCTURE     │
│                 │                 │                         │
│ • products.py   │ • Products      │ • Dependencies          │
│ • stores.py     │   - entities    │ • Database              │
│ • reports.py    │   - services    │ • Authentication        │
│                 │   - repositories│ • Error Handling        │
│                 │   - schemas     │ • Logging               │
│                 │                 │                         │
│                 │ • Stores        │                         │
│                 │ • Reporting     │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Domaines Métier

#### 1. Products Domain
```
/api/v1/products/
├── GET    /           # Liste des produits avec filtres
├── POST   /           # Créer un produit
├── GET    /{id}       # Détails d'un produit
├── PUT    /{id}       # Modifier un produit
└── DELETE /{id}       # Supprimer un produit
```

#### 2. Stores Domain
```
/api/v1/stores/
├── GET    /           # Liste des magasins
├── POST   /           # Créer un magasin
├── GET    /{id}       # Détails d'un magasin
├── PUT    /{id}       # Modifier un magasin
├── DELETE /{id}       # Supprimer un magasin
└── GET    /{id}/stock # Stock du magasin
```

#### 3. Reporting Domain
```
/api/v1/reports/
├── GET    /sales      # Rapports de ventes
├── GET    /inventory  # Rapports d'inventaire
├── GET    /kpis       # Indicateurs clés
└── POST   /custom     # Rapports personnalisés
```

### Authentification et Sécurité

```python
# Token-based authentication
headers = {
    "Authorization": "Bearer your-api-token",
    "Content-Type": "application/json"
}

# Exemple d'utilisation
response = requests.get(
    "http://localhost:8000/api/v1/stores",
    headers=headers
)
```

### Documentation Interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI Schema** : http://localhost:8000/openapi.json

## Déploiement Docker

### Architecture Containerisée

Le projet utilise une architecture Docker avec des containers séparés pour chaque service.

```
┌─────────────────────────────────────────────────────────────┐
│                  DOCKER ARCHITECTURE                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│   WEB CONTAINER │  API CONTAINER  │   EXTERNAL DATABASE     │
│                 │                 │                         │
│ • Flask App     │ • FastAPI       │ • PostgreSQL Server     │
│ • Gunicorn      │ • Gunicorn      │ • External Host         │
│ • Port 8080     │ • Port 8000     │ • Port 5432             │
│ • Health Checks │ • Health Checks │ • Persistent Data       │
│ • Logging       │ • Logging       │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
         ↓                ↓                       ↓
app-multi-magasin-web    api          10.194.32.219:5432 (VM ETS)
```

### Configuration Docker

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # API FastAPI
  api:
    build:
      context: .
      dockerfile: dockerfile.api
      target: production
    container_name: log430-api
    environment:
      - DATABASE_URL=postgresql://user:password@10.194.32.219:5432/store_db
      - LOG_LEVEL=INFO
      - API_TOKEN=your-secret-api-token
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Application Flask
  web:
    build:
      context: .
      dockerfile: dockerfile.flask
      target: production
    container_name: log430-web
    environment:
      - DATABASE_URL=postgresql://user:password@10.194.32.219:5432/store_db
      - API_BASE_URL=http://api:8000
    ports:
      - "8080:8080"
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Dockerfiles Multi-Stage

#### dockerfile.api (FastAPI)
```dockerfile
# Stage de développement
FROM python:3.9-slim as development
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage de production
FROM python:3.9-slim as production
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
RUN mkdir -p logs && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["gunicorn", "src.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### dockerfile.flask (Web App)
```dockerfile
# Stage de production
FROM python:3.9-slim as production
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "src.app.run:app"]
```

### Commandes de Gestion (Makefile)

```bash
# Initialisation
make init          # Créer les répertoires nécessaires

# Gestion des services
make build         # Construire les images Docker
make up            # Démarrer tous les services
make down          # Arrêter tous les services
make restart       # Redémarrer tous les services

# Monitoring
make status        # Voir le statut des services
make logs          # Voir tous les logs
make logs-api      # Logs de l'API uniquement
make logs-web      # Logs de l'app web uniquement

# Maintenance
make clean         # Nettoyer les containers
make test          # Exécuter les tests
make shell-api     # Shell dans le container API
make shell-web     # Shell dans le container Web
```

### Sécurité et Bonnes Pratiques

- **Images multi-stage** : Optimisation de la taille et sécurité
- **Health checks** : Surveillance automatique de la santé des services
- **Volumes read-only** : Code source en lecture seule en production
- **Variables d'environnement** : Configuration externalisée

## Structure du Projet

```
log430-labo-03/
├── Docker & Déploiement
│   ├── docker-compose.yml          # Configuration principale
│   ├── dockerfile.api              # Image FastAPI
│   ├── dockerfile.flask            # Image Flask
│   ├── Makefile                    # Commandes de gestion
│   └── DOCKER_README.md            # Documentation Docker
│
├── API RESTful (FastAPI)
│   └── src/api/
│       ├── main.py                 # Point d'entrée API
│       ├── logging_config.py       # Configuration logging
│       └── v1/
│           ├── api.py              # Router principal
│           ├── dependencies.py     # Dépendances communes
│           ├── errors.py           # Gestion d'erreurs
│           ├── endpoints/          # Endpoints REST
│           │   ├── products.py     # CRUD Produits
│           │   ├── stores.py       # CRUD Magasins
│           │   └── reports.py      # Rapports
│           └── domain/             # Architecture DDD
│               ├── products/       # Domaine Produits
│               │   ├── entities/
│               │   ├── repositories/
│               │   ├── services/
│               │   └── schemas/
│               ├── stores/         # Domaine Magasins
│               └── reporting/      # Domaine Rapports
│
├── Application Web (Flask)
│   └── src/app/
│       ├── __init__.py             # Factory Flask
│       ├── run.py                  # Point d'entrée
│       ├── config.py               # Configuration
│       ├── models/
│       │   └── models.py           # Modèles SQLAlchemy
│       ├── controllers/            # Contrôleurs MVC
│       │   ├── home_controller.py
│       │   ├── magasin_controller.py
│       │   ├── caisse_controller.py
│       │   ├── produit_controller.py
│       │   ├── vente_controller.py
│       │   ├── rapport_controller.py
│       │   └── stock_central_controller.py
│       ├── templates/              # Templates Jinja2
│       │   ├── base.html
│       │   ├── home.html
│       │   ├── rapport/
│       │   ├── magasin/
│       │   ├── caisse/
│       │   ├── produit/
│       │   └── vente/
│       └── static/
│           └── css/
│               └── style.css
│
├── Logging & Monitoring
│   ├── logs/                       # Fichiers de logs
│   │   ├── api_YYYY-MM-DD.log      # Logs API
│   │   ├── business_YYYY-MM-DD.log # Logs métier
│   │   └── errors_YYYY-MM-DD.log   # Logs d'erreurs
│   └── README_LOGGING.md           # Documentation logging
│
├── Tests
│   ├── test_app.py                 # Tests structure
│   ├── test_functionality.py       # Tests fonctionnels
│   └── api/v1/                     # Tests API
│       ├── test_products.py
│       ├── test_stores.py
│       └── test_reports.py
│
├── Documentation
│   ├── docs/
│   │   ├── adr-003-flask.md        # Décision architecture
│   │   ├── adr-004-architecture-mvc.md
│   │   ├── docker-deployment.md    # Guide déploiement
│   │   ├── logging.md              # Documentation logging
│   │   ├── openapi.json            # Spécification API
│   │   └── UML/                    # Diagrammes UML
│   └── README.md                   # Ce fichier
│
└── Configuration
    ├── requirements.txt            # Dépendances Python
    ├── scripts/
    │   └── init-db.sql            # Initialisation DB
    └── src/
        ├── db.py                   # Configuration DB
        └── create_db.py            # Données de démo
```

## Installation et Configuration

### Déploiement Rapide (Docker)

```bash
# 1. Cloner le projet
git clone <repository-url>
cd log430-labo-03

# 2. Initialiser l'environnement
make init

# 3. Démarrer tous les services
make up

# 4. Vérifier le statut
make status
```

**Services disponibles :**
- **Application Web** : http://localhost:8080
- **API REST** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

### Développement Local

#### 1. Prérequis
- Python 3.9+
- PostgreSQL 15+
- Docker & Docker Compose (optionnel)

#### 2. Installation
```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

#### 3. Configuration
Créer le fichier `.env` :
```env
DATABASE_URL=postgresql://user:password@localhost:5432/store_db
SECRET_KEY=your-secret-key-here
API_TOKEN=your-api-token-here
LOG_LEVEL=INFO
POOL_SIZE=5
MAX_OVERFLOW=10
```

#### 4. Base de données
```bash
# Initialiser la base avec des données de démo
python -m src.create_db
```

#### 5. Lancement
```bash
# Terminal 1 : API FastAPI
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 : Application Flask
python -m src.app.run
```

### Configuration Avancée

#### Variables d'Environnement
```bash
# Base de données
DATABASE_URL=postgresql://user:password@host:port/database
POOL_SIZE=5
MAX_OVERFLOW=10

# Sécurité
SECRET_KEY=your-secret-key
API_TOKEN=your-api-token

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Serveur
HOST=0.0.0.0
API_PORT=8000
WEB_PORT=8080
FLASK_ENV=production
```

#### Configuration de Production
```bash
# Optimisations de performance
POOL_SIZE=20
MAX_OVERFLOW=30
WORKERS=4

# Sécurité renforcée
FLASK_ENV=production
DEBUG=False
TESTING=False
```

## Tests

### Tests Automatisés

Le projet inclut une suite complète de tests automatisés couvrant tous les composants.

```bash
# Exécuter tous les tests
make test

# Tests spécifiques
python -m pytest tests/test_app.py -v
python -m pytest tests/api/v1/ -v

# Tests avec couverture
python -m pytest --cov=src tests/
```

### Types de Tests

#### 1. Tests Unitaires
- **Models** : Validation des modèles SQLAlchemy
- **Services** : Logique métier des domaines
- **Repositories** : Accès aux données

#### 2. Tests d'Intégration
- **API Endpoints** : Tests complets des endpoints REST
- **Database** : Tests de persistance
- **Authentication** : Tests de sécurité

#### 3. Tests Fonctionnels
- **Workflows** : Scénarios utilisateur complets
- **Business Logic** : Règles métier
- **Error Handling** : Gestion d'erreurs

### Coverage Report
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/api/main.py                           45      2    96%
src/api/v1/domain/products/services.py   78      5    94%
src/api/v1/domain/stores/services.py     82      6    93%
src/api/v1/domain/reporting/services.py  65      4    94%
src/app/controllers/                     234     12    95%
-----------------------------------------------------------
TOTAL                                   1247     67    95%
```

## Utilisation

### Interface Web (Flask)

#### Dashboard Principal
- **Vue d'ensemble** : KPIs globaux, alertes, tendances
- **Navigation** : Accès rapide aux 5 magasins
- **Monitoring** : Statut en temps réel des caisses

#### Gestion des Ventes
```
1. Sélectionner un magasin
2. Choisir une caisse disponible
3. Rechercher et ajouter des produits
4. Finaliser la vente
5. Imprimer le reçu
```

#### Rapports Stratégiques
- **Performance par magasin** : CA, marge, rotation stock
- **Top produits** : Ventes, popularité, rentabilité
- **Analyse temporelle** : Tendances, saisonnalité
- **Alertes stock** : Ruptures, surstocks, réapprovisionnement

### API RESTful (FastAPI)

#### Authentification
```python
import requests

headers = {
    "Authorization": "Bearer your-api-token",
    "Content-Type": "application/json"
}
```

#### Exemples d'Utilisation

##### Gestion des Produits
```python
# Créer un produit
product_data = {
    "nom": "Nouveau Produit",
    "prix": 29.99,
    "categorie_id": 1,
    "description": "Description du produit"
}
response = requests.post(
    "http://localhost:8000/api/v1/products",
    json=product_data,
    headers=headers
)

# Lister les produits avec filtres
params = {
    "categorie_id": 1,
    "prix_min": 10.0,
    "prix_max": 50.0,
    "limit": 20
}
response = requests.get(
    "http://localhost:8000/api/v1/products",
    params=params,
    headers=headers
)
```

##### Gestion des Magasins
```python
# Obtenir les détails d'un magasin
response = requests.get(
    "http://localhost:8000/api/v1/stores/1",
    headers=headers
)

# Consulter le stock d'un magasin
response = requests.get(
    "http://localhost:8000/api/v1/stores/1/stock",
    headers=headers
)
```

##### Rapports
```python
# Générer un rapport de ventes
params = {
    "date_debut": "2024-01-01",
    "date_fin": "2024-12-31",
    "magasin_id": 1
}
response = requests.get(
    "http://localhost:8000/api/v1/reports/sales",
    params=params,
    headers=headers
)
```

### Monitoring et Logs

#### Consultation des Logs
```bash
# Logs en temps réel
make logs

# Logs spécifiques
make logs-api    # API FastAPI
make logs-web    # Application Flask

# Logs par fichier
tail -f logs/api_2024-06-21.log
tail -f logs/business_2024-06-21.log
tail -f logs/errors_2024-06-21.log
```

#### Métriques de Performance
- **Temps de réponse** : Automatiquement ajouté aux headers HTTP
- **Throughput** : Nombre de requêtes par seconde
- **Erreurs** : Taux d'erreur et types d'exceptions
- **Ressources** : Utilisation CPU/Mémoire des containers

## Technologies Utilisées

### Backend
- **Python 3.9+** : Langage principal
- **Flask 3.0.0** : Framework web pour l'interface utilisateur
- **FastAPI 0.104.1** : Framework API moderne et performant
- **SQLAlchemy 2.0** : ORM pour la gestion des données
- **Pydantic** : Validation et sérialisation des données
- **Gunicorn** : Serveur WSGI/ASGI de production

### Frontend
- **Jinja2** : Moteur de templates
- **Bootstrap 5** : Framework CSS responsive
- **JavaScript ES6+** : Interactions côté client
- **Chart.js** : Graphiques et visualisations

### Base de Données
- **PostgreSQL 15** : Base de données relationnelle
- **psycopg2** : Adaptateur PostgreSQL pour Python
- **Connection Pooling** : Optimisation des connexions

### DevOps & Déploiement
- **Docker** : Containerisation
- **Docker Compose** : Orchestration multi-containers
- **Gunicorn** : Serveur de production
- **Health Checks** : Surveillance des services

### Logging & Monitoring
- **Python Logging** : Système de logs natif
- **Rotating File Handler** : Rotation automatique
- **JSON Logging** : Format structuré pour les logs métier
- **Custom Formatters** : Formatage personnalisé

### Testing & Qualité
- **pytest** : Framework de tests
- **pytest-cov** : Couverture de code
- **Black** : Formatage de code
- **Flake8** : Analyse statique

### Sécurité
- **Token-based Auth** : Authentification par tokens
- **Environment Variables** : Configuration sécurisée
- **Non-root Containers** : Containers sécurisés
- **Input Validation** : Validation stricte des entrées

---

## Support et Contribution

### Issues et Bugs
Pour signaler un bug ou demander une fonctionnalité, veuillez utiliser le système d'issues du projet.

### Documentation
- **API Documentation** : http://localhost:8000/docs
- **Docker Guide** : [DOCKER_README.md](DOCKER_README.md)

### Licence
Ce projet est développé dans le cadre du cours LOG430 à l'ÉTS.

---

**Version** : 3.0.0  
**Dernière mise à jour** : Juin 2025
**Auteur** : Louqman Masbahi
