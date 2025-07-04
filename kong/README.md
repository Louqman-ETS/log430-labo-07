# Kong API Gateway - Microservices DDD

Ce projet utilise Kong comme API Gateway pour gérer l'accès aux microservices à partir d'un point d'entrée unique.

## 🌟 Fonctionnalités implementées

### ✅ **Routage dynamique**
- **Inventory API**: `http://localhost:8000/inventory/*` → `http://inventory-api:8001/*`
- **Retail API**: `http://localhost:8000/retail/*` → `http://retail-api:8002/*`  
- **Ecommerce API**: `http://localhost:8000/ecommerce/*` → `http://ecommerce-api:8000/*`
- **Reporting API**: `http://localhost:8000/reporting/*` → `http://reporting-api:8005/*`

### ✅ **Clés API**
- **Authentification obligatoire** pour tous les endpoints
- **4 consommateurs** prédéfinis avec clés API
- **Protection** contre l'accès non autorisé

### ✅ **Logging centralisé**
- **Logs structurés** pour chaque service
- **Traçabilité** des requêtes avec headers personnalisés
- **Monitoring** des performances et erreurs

## 🚀 Démarrage rapide

### 1. Configuration complète automatique
```bash
make -f Makefile.kong setup-all
```

### 2. Configuration manuelle étape par étape
```bash
# Démarrer les microservices
make -f Makefile.kong services-up

# Démarrer Kong
make -f Makefile.kong kong-up

# Configurer Kong
make -f Makefile.kong kong-setup

# Tester la configuration
make -f Makefile.kong kong-test
```

## 🔑 Clés API disponibles

| Consommateur | Clé API | Usage recommandé |
|--------------|---------|------------------|
| `admin-user` | `admin-api-key-12345` | Administration système |
| `frontend-app` | `frontend-api-key-67890` | Application web frontend |
| `mobile-app` | `mobile-api-key-abcde` | Application mobile |
| `external-partner` | `partner-api-key-fghij` | Partenaires externes |

## 📡 Utilisation des endpoints

### Exemples de requêtes

```bash
# Lister les produits (via Kong)
curl -H "apikey: admin-api-key-12345" \
     http://localhost:8000/inventory/api/v1/products/

# Créer une vente (via Kong)
curl -H "apikey: frontend-api-key-67890" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/retail/api/v1/sales/ \
     -d '{"store_id":1,"cash_register_id":1,"lines":[{"product_id":1,"quantite":2,"prix_unitaire":25.0}]}'

# Obtenir le résumé global (via Kong)
curl -H "apikey: partner-api-key-fghij" \
     http://localhost:8000/reporting/api/v1/reports/global-summary
```

### Comparaison sans Kong

```bash
# AVANT (accès direct aux services)
curl http://localhost:8001/api/v1/products/       # Inventory
curl http://localhost:8002/api/v1/sales/          # Retail
curl http://localhost:8000/api/v1/customers/      # Ecommerce
curl http://localhost:8005/api/v1/reports/        # Reporting

# APRÈS (via Kong avec authentification)
curl -H "apikey: admin-api-key-12345" http://localhost:8000/inventory/api/v1/products/
curl -H "apikey: admin-api-key-12345" http://localhost:8000/retail/api/v1/sales/
curl -H "apikey: admin-api-key-12345" http://localhost:8000/ecommerce/api/v1/customers/
curl -H "apikey: admin-api-key-12345" http://localhost:8000/reporting/api/v1/reports/
```

## 🌐 Interfaces web

### Kong Manager (Interface officielle)
- **URL**: http://localhost:8002
- **Fonctionnalités**: Configuration Kong, monitoring
- **Authentification**: Aucune (développement)

### Konga (Interface communautaire)
- **URL**: http://localhost:1337
- **Fonctionnalités**: Interface graphique avancée
- **Configuration**: Première utilisation nécessite setup

#### Configuration Konga (première fois)
1. Aller sur http://localhost:1337
2. Créer un compte administrateur
3. Ajouter une connexion Kong:
   - **Nom**: `Kong Local`
   - **URL**: `http://kong:8001`

## 📊 Monitoring et logging

### Logs des services
```bash
# Logs Kong
make -f Makefile.kong kong-logs

# Logs en temps réel
make -f Makefile.kong logs-follow

# Logs par service (dans ./logs/)
tail -f logs/inventory-api.log
tail -f logs/retail-api.log
tail -f logs/ecommerce-api.log
tail -f logs/reporting-api.log
```

### Métriques et monitoring
- **Rate limiting**: 100-200 req/min selon le service
- **Headers de traçabilité**: `X-Service-Name`, `X-Gateway`
- **Logs structurés**: JSON avec timestamps, status codes

## 🔧 Configuration avancée

### Plugins activés par service

| Service | Plugins |
|---------|---------|
| **Tous** | `key-auth`, `rate-limiting`, `file-log`, `request-transformer` |
| **Inventory** | 100 req/min, 1000 req/h |
| **Retail** | 100 req/min, 1000 req/h |
| **Ecommerce** | 200 req/min, 2000 req/h |
| **Reporting** | 50 req/min, 500 req/h |

### Modification des limites
```bash
# Via API Admin Kong
curl -X PATCH http://localhost:8001/plugins/{plugin-id} \
     --data "config.minute=200" \
     --data "config.hour=2000"
```

## 🛠️ Commandes utiles

```bash
# Statut du système
make -f Makefile.kong kong-status

# Redémarrage complet
make -f Makefile.kong restart-all

# Nettoyage complet (⚠️ supprime toutes les données)
make -f Makefile.kong kong-clean

# Ouvrir les interfaces web
make -f Makefile.kong kong-gui    # Kong Manager
make -f Makefile.kong konga-gui   # Konga
```

## 🔍 Debugging

### Vérifier la configuration Kong
```bash
# Lister tous les services
curl http://localhost:8001/services

# Lister toutes les routes
curl http://localhost:8001/routes

# Lister tous les consommateurs
curl http://localhost:8001/consumers

# Vérifier les plugins
curl http://localhost:8001/plugins
```

### Tests de connectivité
```bash
# Test complet automatique
make -f Makefile.kong kong-test

# Test manuel d'un service
curl -H "apikey: admin-api-key-12345" \
     http://localhost:8000/inventory/health
```

## 📚 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Client App    │────▶│   Kong Gateway   │────▶│  Microservices  │
│                 │     │                  │     │                 │
│ • Frontend      │     │ • Route requests │     │ • inventory-api │
│ • Mobile        │     │ • Authenticate   │     │ • retail-api    │
│ • External API  │     │ • Rate limiting  │     │ • ecommerce-api │
│                 │     │ • Logging        │     │ • reporting-api │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 🎯 Avantages de cette architecture

### ✅ **Point d'entrée unique**
- Une seule URL pour tous les services
- Gestion centralisée de l'authentification
- Routage transparent vers les microservices

### ✅ **Sécurité renforcée**
- Authentification obligatoire par clé API
- Rate limiting pour prévenir les abus
- Isolation des services backend

### ✅ **Observabilité**
- Logging centralisé de toutes les requêtes
- Métriques de performance
- Traçabilité des appels

### ✅ **Scalabilité**
- Load balancing automatique
- Gestion des timeouts
- Configuration dynamique

## 🚨 Notes importantes

1. **Ports Kong**: Kong utilise les ports 8000-8002, assurez-vous qu'ils sont libres
2. **Réseau Docker**: Kong et les microservices doivent être sur le même réseau
3. **Ordre de démarrage**: Les microservices doivent être démarrés avant Kong
4. **Configuration**: Les modifications de configuration nécessitent un redémarrage

## 📞 Support

Pour les problèmes de configuration Kong:
1. Vérifier les logs: `make -f Makefile.kong kong-logs`
2. Vérifier le statut: `make -f Makefile.kong kong-status`
3. Tester la configuration: `make -f Makefile.kong kong-test`
4. En cas de problème majeur: `make -f Makefile.kong restart-all` 