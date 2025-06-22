# 🐳 Déploiement Docker - LOG430-Labo-03

## 🏗️ Architecture

Le projet utilise **3 containers séparés** :

- **`db`** : PostgreSQL 15 (base de données)
- **`api`** : FastAPI (API RESTful)  
- **`web`** : Flask (interface web)

## 🚀 Démarrage Rapide

### 1. Première utilisation
```bash
# Initialiser le projet
make init

# Créer un fichier .env (optionnel)
cp .env.example .env

# Construire et démarrer
make up
```

### 2. Utilisation quotidienne
```bash
# Démarrer tous les services
make up

# Voir les logs
make logs

# Arrêter les services
make down
```

## 🌐 Accès aux Services

- **Application Web** : http://localhost:8080
- **API FastAPI** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Base de données** : localhost:5432

## 📋 Commandes Utiles

```bash
# Voir toutes les commandes disponibles
make help

# Construire les images
make build

# Voir le statut des services
make status

# Voir les logs d'un service spécifique
make logs-api
make logs-web  
make logs-db

# Ouvrir un shell dans un container
make shell-api
make shell-web
make shell-db

# Exécuter les tests
make test

# Sauvegarder la base de données
make backup-db

# Nettoyer les containers
make clean
```

## ⚙️ Configuration

### Variables d'environnement (.env)
```bash
# Base de données
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=store_db
DB_PORT=5432

# API
API_PORT=8000
API_TOKEN=your-secret-token
LOG_LEVEL=INFO

# Application web
WEB_PORT=8080
```

### Ports utilisés
- **8080** : Application Flask
- **8000** : API FastAPI
- **5432** : PostgreSQL

## 📊 Volumes et Données

### Volume de base de données
- **Volume** : `postgres_data`
- **Persistance** : Les données survivent aux redémarrages
- **Sauvegarde** : `make backup-db`

### Volume de logs
- **Répertoire** : `./logs`
- **Contenu** : Logs de l'API FastAPI

## 🔧 Développement vs Production

### Mode développement
```bash
# Démarrage avec rechargement automatique
make up-dev
```

### Mode production
```bash
# Démarrage optimisé
make up
```

## 🛠️ Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Modifier les ports dans .env
   API_PORT=8001
   WEB_PORT=8081
   ```

2. **Base de données non accessible**
   ```bash
   # Vérifier le statut
   make status
   
   # Voir les logs
   make logs-db
   ```

3. **Problème de build**
   ```bash
   # Nettoyer et reconstruire
   make clean
   make build
   ```

## 🔒 Sécurité

- **Utilisateurs non-root** dans les containers
- **Volumes read-only** pour le code source
- **Health checks** pour tous les services
- **Réseau isolé** pour les communications internes

## 📈 Monitoring

### Health checks
- Tous les services ont des health checks automatiques
- Vérification toutes les 30 secondes
- Redémarrage automatique en cas de problème

### Logs
- Logs centralisés avec Docker Compose
- Rotation automatique des logs
- Formats structurés pour l'analyse

---

## 🎯 Utilisation Recommandée

### Pour le développement :
```bash
make up-dev     # Démarrage avec rechargement
make logs       # Surveillance des logs
```

### Pour la production :
```bash
make up         # Démarrage optimisé
make status     # Vérification du statut
make backup-db  # Sauvegarde régulière
```

### Pour les tests :
```bash
make test       # Tests automatisés
make clean      # Nettoyage après tests
``` 