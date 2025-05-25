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

docker-compose.yml         # Déploiement local (dev)
docker-compose.server.yml  # Serveur PostgreSQL uniquement
docker-compose.client.yml  # Application uniquement
```

## Déploiement

### Option 1: Local (Développement)

```bash
# Tout sur la même machine
docker-compose up --build
docker exec -it caisse-magasin python -m src.main
```

### Option 2: Distribué (Production)

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

### Variables d'environnement

```env
DATABASE_URL=postgresql://user:password@HOST:5432/store_db
POOL_SIZE=5
MAX_OVERFLOW=10
```

### Connexion Base de Données

- **Host** : IP du serveur PostgreSQL
- **Port** : 5432
- **Database** : store_db
- **User** : user
- **Password** : password

## Utilisation

### Menu Principal

1. Sélectionner une caisse (1, 2 ou 3)
2. Nouvelle vente
3. Ajouter produits (recherche par nom/code/ID)
4. Finaliser vente (génère reçu)
5. Retour de produits
6. Recherche produits par catégorie

### Données Pré-chargées

- **4 catégories** : Alimentaire, Boissons, Hygiène, Ménage
- **25+ produits** avec codes, prix et stock
- **3 caisses** disponibles

## Tests

```bash
# Démarrer PostgreSQL
docker-compose up -d db

# Lancer les tests
export DATABASE_URL="postgresql://user:password@localhost:5432/store_db"
python -m tests.run_tests
```

## Commandes Utiles

```bash
# Voir les conteneurs
docker-compose ps

# Logs
docker-compose logs caisse-app
docker-compose logs db

# Arrêter
docker-compose down

# Reset complet (supprime données)
docker-compose down -v

# Accès direct PostgreSQL
docker exec -it log430-labo-01_db_1 psql -U user -d store_db
```

## Dépendances

- **SQLAlchemy 2.0.23** - ORM
- **psycopg2-binary 2.9.9** - Driver PostgreSQL
- **python-dotenv 1.0.0** - Variables d'environnement
