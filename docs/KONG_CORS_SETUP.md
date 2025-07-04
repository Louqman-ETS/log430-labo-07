# Configuration CORS Kong - Approche Déclarative

## Vue d'ensemble

Cette configuration utilise l'approche **déclarative** de Kong pour configurer CORS de manière persistante et reproductible. Tous les paramètres sont définis dans des fichiers YAML versionnés dans Git.

## Fichiers de Configuration

```
kong/
├── kong-declarative.yml    # Configuration complète Kong avec CORS
├── apply-config.sh         # Script d'application de la configuration
└── README.md              # Ce fichier

test-cors.sh               # Script de test CORS
```

## Démarrage Rapide

### 1. Démarrer Kong
```bash
make -f Makefile.kong kong-up
```

### 2. Appliquer la configuration CORS
```bash
chmod +x kong/apply-config.sh
./kong/apply-config.sh
```

### 3. Tester CORS
```bash
chmod +x test-cors.sh
./test-cors.sh
```

## Configuration CORS Incluse

### Origins Autorisés
- `http://localhost:3000` - Application React/Vue.js de développement
- `http://localhost:8080` - Application alternative
- `http://localhost:5000` - Application Flask/autre framework
- `https://yourdomain.com` - Domaine de production
- `*` - Wildcard (à restreindre en production)

### Méthodes HTTP
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`

### Headers Autorisés
- Standards: `Accept`, `Content-Type`, `Content-Length`
- Authentification: `Authorization`, `apikey`, `X-Auth-Token`
- Tracking: `X-Request-ID`, `X-Instance-ID`

### Headers Exposés
- `X-Auth-Token` - Token d'authentification
- `X-Request-ID` - ID de requête pour le tracking
- `X-Instance-ID` - ID de l'instance (load balancing)
- `X-RateLimit-Limit` - Limite de taux
- `X-RateLimit-Remaining` - Requêtes restantes

### Autres Paramètres
- **Credentials**: `true` - Permet l'envoi de cookies et headers d'auth
- **Max-Age**: `3600` secondes - Cache des requêtes preflight
- **Preflight Continue**: `false` - Kong gère les requêtes OPTIONS

## Services et Routes Configurés

| Service | Route | URL Backend | CORS |
|---------|--------|-------------|------|
| inventory-api | `/inventory` | `http://inventory-api:8001` | Oui |
| ecommerce-api | `/ecommerce` | `http://ecommerce-api:8000` | Oui |
| retail-api | `/retail` | `http://retail-api:8002` | Oui |
| reporting-api | `/reporting` | `http://reporting-api:8005` | Oui |

## Authentification

### Consommateurs et Clés API
- **admin-user**: `admin-api-key-12345`
- **frontend-app**: `frontend-api-key-67890`
- **mobile-app**: `mobile-api-key-abcde`
- **external-partner**: `partner-api-key-fghij`

### Utilisation
```bash
curl -H "apikey: admin-api-key-12345" \
     -H "Origin: http://localhost:3000" \
     http://localhost:9000/inventory/api/v1/products/
```

## Load Balancing

L'upstream `inventory-api-upstream` est configuré pour le load balancing :
- **Algorithme**: Round-robin
- **Health checks**: Actifs sur `/health`
- **Targets**: `inventory-api-1`, `inventory-api-2`, `inventory-api-3`

Pour utiliser le load balancing, modifiez le service inventory-api dans `kong-declarative.yml` :
```yaml
services:
  - name: inventory-api
    url: http://inventory-api-upstream:8001  # Utilise l'upstream
```

## Tests

### Test Automatique
```bash
./test-cors.sh
```

### Tests Manuels

#### Requête Preflight
```bash
curl -X OPTIONS http://localhost:9000/inventory/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

#### Requête avec CORS
```bash
curl -H "Origin: http://localhost:3000" \
     -H "apikey: admin-api-key-12345" \
     http://localhost:9000/inventory/api/v1/products/ \
     -v
```

#### Vérifier la Configuration
```bash
# Voir les services
curl -s http://localhost:9001/services | jq '.data[] | {name: .name, url: .url}'

# Voir les plugins CORS
curl -s http://localhost:9001/plugins | jq '.data[] | select(.name == "cors")'
```

## Modification de la Configuration

### 1. Éditer le fichier
```bash
vim kong/kong-declarative.yml
```

### 2. Appliquer les changements
```bash
./kong/apply-config.sh
```

### 3. Tester
```bash
./test-cors.sh
```

## Avantages de cette Approche

### **Persistance**
- Configuration sauvegardée dans des fichiers
- Survit aux redémarrages de Kong
- Versionnée avec Git

### **Reproductibilité**
- Même configuration sur tous les environnements
- Déploiement automatisable
- Infrastructure as Code

### **Maintenance**
- Facile à modifier et réviser
- Historique des changements
- Collaboration d'équipe

### **Sécurité**
- Configuration explicite et visible
- Validation possible avant déploiement
- Rollback facile

## Sécurité en Production

Pour la production, modifiez `kong-declarative.yml` :

```yaml
# Restreindre les origins
origins:
  - "https://app.mondomaine.com"
  - "https://admin.mondomaine.com"

# Supprimer le wildcard
# - "*"  # À supprimer en production

# Limiter les méthodes si nécessaire
methods:
  - GET
  - POST
  - PUT
  - DELETE
  # - OPTIONS  # Gardé pour CORS
```

## Ressources

- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [Kong CORS Plugin](https://docs.konghq.com/hub/kong-inc/cors/)
- [CORS MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

## Prochaines Étapes

1. **Environnement de test** : Adapter les origins pour l'environnement de test
2. **Production** : Restreindre les origins et supprimer le wildcard
3. **Monitoring** : Ajouter des métriques CORS spécifiques
4. **Automation** : Intégrer dans un pipeline CI/CD 