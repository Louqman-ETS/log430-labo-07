# Système de Caisse de Magasin - LOG430 Laboratoire 1

Application Python console conforme au laboratoire 1 du cours LOG430.

## Description

Ce système simule une caisse de magasin avec une architecture client/serveur où:
- Le client est une application console Python
- Le serveur est une base de données SQLite locale accédée via SQLAlchemy
- Les données sont persistantes grâce à un volume Docker dédié

L'application permet de:
- Sélectionner une des 3 caisses disponibles
- Créer des ventes (transactions)
- Rechercher des produits par ID, nom, code ou catégorie
- Gérer des transactions simultanées de manière cohérente
- Effectuer des retours de produits
- Conserver les données entre les redémarrages

## Structure du projet

```
src/
  ├── models.py    - Définition des entités (Produit, Categorie, etc.)
  ├── db.py        - Configuration de la base de données SQLite
  ├── dao.py       - Couche d'accès aux données
  ├── service.py   - Logique métier et services
  ├── main.py      - Application console
  └── create_db.py - Script d'initialisation de la base de données
```

## Prérequis

- Python 3.6+
- SQLAlchemy
- SQLite

Ou alternativement:
- Docker et Docker Compose

## Installation

### Installation standard

1. Clonez ce dépôt:
   ```
   git clone [URL_DU_DEPOT]
   cd log430-labo-01
   ```

2. Créez un environnement virtuel et activez-le:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Sur Linux/macOS
   # ou
   .venv\Scripts\activate     # Sur Windows
   ```

3. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

4. Initialisez la base de données:
   ```
   python -m src.create_db
   ```

### Installation avec Docker

1. Clonez ce dépôt:
   ```
   git clone [URL_DU_DEPOT]
   cd log430-labo-01
   ```

2. Construisez l'image Docker:
   ```
   docker compose build
   ```

## Utilisation

### Lancement standard

1. Activez l'environnement virtuel:
   ```
   source .venv/bin/activate  # Sur Linux/macOS
   # ou
   .venv\Scripts\activate     # Sur Windows
   ```

2. Lancez l'application:
   ```
   python -m src.main
   ```

### Lancement avec Docker

Pour lancer l'application en mode interactif (recommandé):
```
docker compose run --rm caisse-app
```

Cette commande lance l'application dans votre terminal et vous permet d'interagir directement avec elle. Les données sont automatiquement persistées dans un volume Docker nommé `db-data`.

Pour lancer l'application en arrière-plan:
```
docker compose up -d
```

Pour voir les logs:
```
docker logs caisse-magasin
```

Pour arrêter l'application:
```
docker compose down
```

Note: L'option `--rm` n'est plus nécessaire car les données sont maintenant persistées dans le volume Docker.

## Fonctionnalités

- **Recherche de produits**: Par ID, nom, code ou catégorie
- **Gestion des ventes**: Création, ajout de produits, finalisation
- **Retour de produits**: Permet de retourner des produits vendus (mise à jour du stock)
- **Catégories prédéfinies**: Alimentaire, Boissons, Hygiène, Ménage
- **Transactions**: Garantit la cohérence des données même lors de ventes simultanées

## Architecture

L'application utilise une architecture en couches:
- **Présentation**: Interface console dans `main.py`
- **Logique métier**: Services dans `service.py`
- **Accès aux données**: DAO dans `dao.py`
- **Modèles**: Entités dans `models.py`
- **Persistance**: Configuration SQLAlchemy dans `db.py`

## Considérations techniques

- Les transactions sont gérées via SQLAlchemy pour assurer la cohérence des données
- Le système est conçu pour gérer plusieurs caisses travaillant en parallèle
- La base de données est initialisée avec des données de test uniquement si elle est vide
- Les données sont persistantes entre les redémarrages grâce au volume Docker
- La base de données utilise le mode WAL (Write-Ahead Logging) de SQLite pour une meilleure performance et fiabilité
- Utilisation de Docker pour faciliter le déploiement et garantir un environnement consistant
