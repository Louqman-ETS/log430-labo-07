# Système Multi-Magasins - LOG430

Application web Flask pour la gestion de points de vente multi-magasins avec reporting stratégique et gestion centralisée des stocks.

## Table des Matières

- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Architecture](#architecture)
- [Cas d'Utilisation](#cas-dutilisation)
- [Structure du Projet](#structure-du-projet)
- [Installation et Configuration](#installation-et-configuration)
- [Tests](#tests)
- [Utilisation](#utilisation)
- [Technologies Utilisées](#technologies-utilisées)

## Fonctionnalités Principales

- **Dashboard multi-magasins** : Vue d'ensemble de 5 magasins avec navigation intuitive
- **Rapports stratégiques** : KPIs globaux, performance par magasin, top produits, tendances
- **Point de vente complet** : Recherche produits, gestion panier, reçus, retours
- **Gestion stocks** : Stocks par magasin, alertes automatiques, réapprovisionnement
- **Interface responsive** : Bootstrap, architecture 3-tiers (Navigateur → Flask → PostgreSQL)

## Architecture

### Architecture MVC 3-Tiers

```
┌─────────────────────────────────────────────────────────────┐
│                ARCHITECTURE 3-TIERS MVC                    │
├─────────────────────┬───────────────┬───────────────────────┤
│    PRESENTATION     │   APPLICATION │        DONNÉES        │
│      (Tier 1)       │    (Tier 2)   │      (Tier 3)         │
│                     │               │                       │
│ • Navigateur Web    │ • Flask App   │ • PostgreSQL          │
│ • Templates HTML    │ • Controllers │ • Base distante       │
│ • Bootstrap CSS     │ • Models      │ • 5 Magasins         │
│ • JavaScript        │ • Business    │ • 15 Caisses         │
│                     │   Logic       │ • Stocks/magasin      │
└─────────────────────┴───────────────┴───────────────────────┘
         ↑                     ↑                     ↑
    HTTP/HTTPS              Flask                PostgreSQL
    Port 8080              Routes                Port 5432
```

**Composants MVC** :
- **Model** : Modèles SQLAlchemy (9 entités), gestion PostgreSQL
- **View** : Templates Jinja2, Bootstrap responsive, JavaScript
- **Controller** : 7 contrôleurs Flask avec blueprints
- **Déploiement** : Docker multi-conteneurs

### Déploiement Docker

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Navigateur    │    │  Container      │    │  Container      │
│     Web         │───▶│    Flask        │───▶│  PostgreSQL     │
│                 │    │   (Client)      │    │   (Serveur)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     Port 8080              Port 8080             Port 5432
```



## Cas d'Utilisation

### Pour Gestionnaire Maison Mère
1. **UC1 - Générer Rapport Consolidé** : Ventes par magasin, top produits, stocks
2. **UC3 - Tableau de Bord Performances** : CA, alertes rupture, surchauffe, tendances
3. **UC8 - Interface Web Minimale** : Accès distant aux indicateurs clés

### Pour Employé Magasin
4. **UC2 - Gestion Stock central & Réapprovisionnement** : Consultation stock central, demandes
5. **Effectuer Vente** : Point de vente complet avec panier et reçu
6. **Traiter Retour** : Retours produits avec remise en stock
7. **Gérer Stock Magasin** : Consultation et mise à jour stocks locaux

## Structure du Projet

```
├── src/
│   ├── app/
│   │   ├── __init__.py              # Application Flask factory
│   │   ├── run.py                   # Point d'entrée principal
│   │   ├── config.py                # Configuration environnement
│   │   ├── models/
│   │   │   └── models.py            # 9 modèles SQLAlchemy
│   │   ├── controllers/             # 7 contrôleurs MVC
│   │   │   ├── home_controller.py           # Dashboard & accueil
│   │   │   ├── magasin_controller.py        # Gestion magasins
│   │   │   ├── caisse_controller.py         # Gestion caisses
│   │   │   ├── produit_controller.py        # Gestion produits
│   │   │   ├── vente_controller.py          # Point de vente
│   │   │   ├── rapport_controller.py        # Rapports stratégiques
│   │   │   └── stock_central_controller.py  # Stock central
│   │   ├── templates/               # Templates HTML organisés
│   │   │   ├── home.html            # Dashboard principal
│   │   │   ├── rapport/             # Module rapports
│   │   │   ├── magasin/             # Module magasins
│   │   │   ├── caisse/              # Module caisses
│   │   │   ├── produit/             # Module produits
│   │   │   └── vente/               # Module point de vente
│   │   └── static/                  # CSS, JS, images
│   ├── db.py                        # Configuration SQLAlchemy
│   └── create_db.py                 # Initialisation données de démo
├── docs/
│   └── UML/                         # Diagrammes UML PlantUML
│       ├── diagramme_deploiement.puml
│       ├── diagramme_cas_utilisation.puml
│       ├── diagarmme_classes.puml
│       ├── diagramme_composants.puml
│       ├── sequence_UC01_Generer_Rapport.puml
│       ├── sequence_UC02_Stock_Reapprovisionnement.puml
│       ├── sequence_UC03_Tableau_Bord.puml
│       └── sequence_UC08_Interface_Web.puml
├── tests/                           # Tests automatisés (23 tests)
│   ├── test_app.py                  # Tests structure application
│   ├── test_functionality.py        # Tests fonctionnalités métier
│   └── run_tests.py                 # Runner de tests
├── docker-compose.server.yml        # PostgreSQL (serveur)
├── docker-compose.client.yml        # Flask App (client)
├── requirements.txt                 # Dépendances Python
└── README.md                        # Documentation projet
```

## Installation et Configuration

### Option 1: Déploiement Docker (Recommandé)

#### Sur le Serveur (Base de données)

```bash
# Démarrer PostgreSQL avec docker-compose
docker-compose -f docker-compose.server.yml up -d

# Vérifier le statut
docker-compose -f docker-compose.server.yml ps
```

#### Sur le PC Client (Application Flask)

```bash
# 1. Configurer l'IP du serveur PostgreSQL dans docker-compose.client.yml
# Modifier la variable DATABASE_URL avec l'IP correcte

# 2. Démarrer l'application web Flask
docker-compose -f docker-compose.client.yml up -d

# 3. Accéder à l'application
# Navigateur: http://localhost:8080
```

### Option 2: Développement Local

#### 1. Installation des dépendances

```bash
# Créer un environnement virtuel Python
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate # Windows

# Installer toutes les dépendances
pip install -r requirements.txt
```

#### 2. Configuration de la base de données

Créer le fichier `.env` à la racine :
```env
DATABASE_URL=postgresql://user:password@HOST:5432/store_db
SECRET_KEY=your-secret-key-here
POOL_SIZE=5
MAX_OVERFLOW=10
```

#### 3. Initialisation des données de démo

```bash
# Créer les tables et insérer les données
python -m src.create_db

# Données créées :
# - 5 magasins (Paris, Lyon, Marseille, Toulouse, Nice)
# - 15 caisses (3 par magasin)
# - 50+ produits avec stocks par magasin
# - Ventes de démo pour les rapports
```

#### 4. Lancement de l'application

```bash
# Démarrer le serveur web Flask
python -m src.app.run

# Application disponible sur: http://127.0.0.1:8080
```

## Tests

### Suite de Tests Complète (23 tests)

```bash
# Lancer tous les tests automatisés
python -m tests.run_tests

# Tests par module
python -m tests.test_app              # Structure Flask & blueprints
python -m tests.test_functionality    # Logique métier & fonctionnalités

# Avec verbosité détaillée
python -m tests.test_app -v
```

### Couverture des Tests

- ✅ **Structure Application** : Imports, création Flask, configuration
- ✅ **Modèles de Données** : 9 modèles SQLAlchemy validés
- ✅ **Contrôleurs** : 7 blueprints fonctionnels testés
- ✅ **Base de Données** : Connexions et pool
- ✅ **Logique Métier** : Calculs rapports, gestion stocks, ventes

## Utilisation

### Dashboard Principal (`/`)

**Vue d'ensemble** :
- Liste des 5 magasins avec leur statut
- Accès rapide aux modules principaux
- Navigation claire entre fonctionnalités

### Module Rapports Stratégiques (`/rapport`)

**KPIs Globaux** :
- Chiffre d'affaires total consolidé
- Nombre de transactions et panier moyen
- Performance comparative des magasins

**Analyses Détaillées** :
- Classement magasins avec badges de couleur
- Top 15 produits les plus vendus
- Alertes stock avec recommandations d'action
- Tendances sur 7 jours avec graphiques
- Filtrage par magasin pour analyses ciblées

### Point de Vente (`/magasin/{id}/caisse/{id}/nouvelle-vente`)

**Processus de Vente** :
1. **Recherche produits** : Nom, code-barres, catégorie
2. **Gestion panier** : Ajout, modification quantités, suppression
3. **Calculs automatiques** : Sous-totaux, total TTC
4. **Finalisation** : Génération reçu détaillé, mise à jour stocks

**Retours** (`/retours`) :
- Liste des ventes récentes par magasin
- Sélection produits à retourner
- Remise en stock automatique

### Gestion des Stocks

**Stock Central** (`/stock-central`) :
- Vue consolidée tous magasins
- Seuils d'alerte configurables
- Mouvements de stock en temps réel

**Stock par Magasin** (`/magasin/{id}/produits`) :
- Stocks spécifiques au magasin
- Badges colorés selon niveaux
- Demandes de réapprovisionnement

## Dépannage

### Erreurs Courantes

**Erreur de connexion PostgreSQL** :
```bash
# Vérifier que le serveur PostgreSQL fonctionne
docker-compose -f docker-compose.server.yml ps

# Vérifier les logs
docker-compose -f docker-compose.server.yml logs db

# Tester la connexion
psql -h SERVER_IP -U user -d store_db
```

**Application Flask ne démarre pas** :
```bash
# Vérifier les dépendances
pip list | grep -E "(Flask|SQLAlchemy|psycopg2)"

# Vérifier la configuration
echo $DATABASE_URL

# Logs détaillés
FLASK_DEBUG=1 python -m src.app.run
```

## Commandes Utiles

### Application Web
```bash
# Lancement standard
python3 -m src.app.run

# Mode debug avec rechargement automatique
FLASK_DEBUG=1 python3 -m src.app.run

# Réinitialiser les données
python3 -m src.create_db
```

### Docker
```bash
# Statut des conteneurs
docker-compose -f docker-compose.client.yml ps

# Logs application Flask
docker-compose -f docker-compose.client.yml logs caisse-app

# Logs base de données
docker-compose -f docker-compose.server.yml logs db

# Redémarrer application
docker-compose -f docker-compose.client.yml restart

# Arrêter tous les services
docker-compose -f docker-compose.client.yml down
docker-compose -f docker-compose.server.yml down
```

## Technologies Utilisées

### Backend
- **Flask 3.0+** - Framework web Python léger et modulaire
- **SQLAlchemy 2.0+** - ORM moderne avec support des requêtes avancées
- **psycopg2-binary** - Driver PostgreSQL optimisé
- **Flask-SQLAlchemy** - Intégration seamless Flask/SQLAlchemy

### Frontend
- **Bootstrap 5** - Framework CSS responsive et moderne
- **Jinja2** - Moteur de templates puissant avec héritage
- **HTML5/CSS3** - Standards web modernes
- **JavaScript** - Interactions dynamiques côté client

### Base de Données
- **PostgreSQL 13+** - Base relationnelle robuste et performante
- **Architecture décentralisée** - Stocks par magasin avec consolidation

### Tests & Qualité
- **unittest** - Framework de tests Python natif
- **unittest.mock** - Mocking pour tests isolés et rapides
- **Coverage** - 23 tests couvrant structure et fonctionnalités

### Déploiement & Ops
- **Docker** - Containerisation pour déploiement simplifié
- **docker-compose** - Orchestration multi-conteneurs
- **Architecture 3-tiers** - Séparation claire des responsabilités

### Documentation
- **PlantUML** - Diagrammes UML pour architecture
- **Markdown** - Documentation technique complète

---

**Projet LOG430 - Laboratoire 02**  
**Auteur** : Louqman Masbahi  
**Architecture** : Système Multi-Magasins Flask MVC 3-Tiers
