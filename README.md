# Système de Caisse de Magasin - LOG430

Application de caisse de magasin avec architecture client/serveur 2-tier utilisant PostgreSQL.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   PC Client     │    │    Serveur      │
│                 │    │                 │
│  Application    │◄──►│   PostgreSQL    │
│  Python Console │    │   Base données  │
└─────────────────┘    └─────────────────┘
```

- **Client** : Application Python console interactive
- **Serveur** : Base de données PostgreSQL
- **Communication** : SQLAlchemy ORM + psycopg2

## Structure du Projet

```
src/
├── main.py          # Point d'entrée de l'application
├── db.py            # Configuration base de données
├── models.py        # Modèles SQLAlchemy (tables)
├── dao.py           # Accès aux données
├── service.py       # Logique métier
└── create_db.py     # Initialisation données

tests/
├── test_dao.py      # Tests des DAOs
├── test_service.py  # Tests des services
├── test_models.py   # Tests des modèles
├── test_config.py   # Configuration des tests
└── run_tests.py     # Script de lancement des tests

docker-compose.yml         # Déploiement local (dev)
docker-compose.server.yml  # Serveur PostgreSQL uniquement
docker-compose.client.yml  # Application uniquement
```

## Installation et Configuration

### Prérequis

- Python 3.11+
- PostgreSQL 13+ (local ou distant)

### Option 1: Développement Local (Sans Docker)

#### 1. Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

#### 2. Configuration de la base de données

**Option A: Base de données locale**
```bash
# Installer PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Créer la base de données
sudo -u postgres psql
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE store_db;
GRANT ALL PRIVILEGES ON DATABASE store_db TO "user";
\q
```

**Option B: Connexion à une base distante**
```bash
# Créer le fichier .env à la racine du projet
cat > .env << EOF
DATABASE_URL=postgresql://user:password@10.194.32.219:5432/store_db
POOL_SIZE=5
MAX_OVERFLOW=10
EOF
```

#### 3. Initialisation des données

```bash
# Initialiser la base de données et les données
python -m src.create_db
```

#### 4. Lancement de l'application

```bash
python -m src.main
```

### Option 2: Docker Local (Développement)

```bash
# Tout sur la même machine
docker-compose up --build
docker exec -it caisse-magasin python -m src.main
```

### Option 3: Déploiement Distribué (Production)

#### Sur le Serveur (Base de données)

```bash
# Démarrer PostgreSQL
docker-compose -f docker-compose.server.yml up -d

# Vérifier
docker-compose -f docker-compose.server.yml ps
```

#### Sur le PC Client (Application)

```bash
# 1. Modifier docker-compose.client.yml
# Remplacer SERVER_IP par l'IP réelle du serveur

# 2. Démarrer l'application
docker-compose -f docker-compose.client.yml up -d

# 3. Utiliser l'application
docker exec -it caisse-magasin-client python -m src.main
```

## Configuration

### Variables d'environnement (.env)

```env
# Configuration de la base de données
DATABASE_URL=postgresql://user:password@HOST:5432/store_db

# Configuration du pool de connexions
POOL_SIZE=5
MAX_OVERFLOW=10
```

### Connexion Base de Données

- **Host** : IP du serveur PostgreSQL (localhost pour local)
- **Port** : 5432
- **Database** : store_db
- **User** : user
- **Password** : password

## Tests

### Lancement des tests

```bash
# Option 1: Avec le script personnalisé
PYTHONPATH=./src python -m tests.run_tests

# Option 2: Avec pytest
PYTHONPATH=./src python -m pytest tests/ -v

# Option 3: Tests spécifiques
PYTHONPATH=./src python -m pytest tests/test_service.py -v
```

### Configuration des tests

Les tests utilisent la même base de données que l'application. Assurez-vous que :
- PostgreSQL est en cours d'exécution
- La variable `DATABASE_URL` est correctement configurée
- La base de données est accessible

## Utilisation

### Menu Principal

1. **Sélectionner une caisse** (1, 2 ou 3)
2. **Nouvelle vente**
3. **Ajouter produits** (recherche par nom/code/ID)
4. **Finaliser vente** (génère reçu)
5. **Retour de produits**
6. **Recherche produits** par catégorie

### Données Pré-chargées

- **4 catégories** : Alimentaire, Boissons, Hygiène, Ménage
- **25+ produits** avec codes, prix et stock
- **3 caisses** disponibles

### Fonctionnalités

- ✅ Gestion des ventes multi-produits
- ✅ Recherche de produits (nom, code, ID)
- ✅ Gestion du stock en temps réel
- ✅ Génération de reçus détaillés
- ✅ Retour de produits avec remise en stock
- ✅ Interface console intuitive

## Dépannage

### Erreurs courantes

**Erreur de connexion à la base de données**
```bash
# Vérifier que PostgreSQL est en cours d'exécution
sudo service postgresql status

# Vérifier la configuration
echo $DATABASE_URL
```

**Erreur "SessionLocal is not defined"**
```bash
# S'assurer que les dépendances sont installées
pip install -r requirements.txt

# Vérifier le PYTHONPATH
export PYTHONPATH=./src
```

**Tests qui échouent**
```bash
# Nettoyer et réinitialiser la base de données
python -m src.create_db
```

## Commandes Utiles

```bash
# Voir les conteneurs (si Docker)
docker-compose ps

# Logs
docker-compose logs caisse-app
docker-compose logs db

# Arrêter
docker-compose down

# Reset complet (supprime données)
docker-compose down -v

# Accès direct PostgreSQL
psql -h localhost -U user -d store_db
# ou avec Docker
docker exec -it log430-labo-01_db_1 psql -U user -d store_db
```

## Dépendances

- **SQLAlchemy 2.0.23** - ORM
- **psycopg2-binary 2.9.9** - Driver PostgreSQL
- **python-dotenv 1.0.0** - Variables d'environnement
- **pytest 8.0.0** - Framework de tests
- **black 24.4.2** - Formatage de code
