# Système de Logging - LOG430-Labo-03

## Vue d'ensemble

Le système de logging de l'API FastAPI est conçu pour fournir une traçabilité complète des opérations, des erreurs et des performances. Il utilise la bibliothèque standard `logging` de Python avec une configuration avancée.

## Architecture du Logging

### Fichiers de Configuration

- **`src/api/logging_config.py`** : Configuration principale du système de logging
- **Répertoire `logs/`** : Stockage des fichiers de logs (créé automatiquement)

### Types de Logs

1. **Logs d'API** (`api_YYYY-MM-DD.log`)
   - Requêtes HTTP entrantes et sortantes
   - Temps de réponse et codes de statut
   - Opérations des endpoints

2. **Logs Business** (`business_YYYY-MM-DD.log`)
   - Opérations métier (CRUD)
   - Format JSON structuré
   - Traçabilité des actions utilisateur

3. **Logs d'Erreurs** (`errors_YYYY-MM-DD.log`)
   - Erreurs et exceptions
   - Stack traces complètes
   - Contexte d'erreur

## Configuration

### Variables d'Environnement

```bash
# Niveau de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Token d'API pour les tests
API_TOKEN=your-secret-api-token-here
```

### Niveaux de Logging

- **DEBUG** : Informations détaillées pour le développement
- **INFO** : Informations générales sur le fonctionnement
- **WARNING** : Situations potentiellement problématiques
- **ERROR** : Erreurs qui nécessitent une attention

## Loggers Spécialisés

### Loggers par Composant

```python
# Logger principal de l'API
logger = get_logger("api")

# Loggers par domaine
endpoints_logger = get_logger("api.endpoints")
services_logger = get_logger("api.services")
repositories_logger = get_logger("api.repositories")
auth_logger = get_logger("api.auth")
errors_logger = get_logger("api.errors")

# Loggers par module métier
stores_logger = get_logger("api.endpoints.stores")
products_logger = get_logger("api.endpoints.products")
reports_logger = get_logger("api.endpoints.reports")
```

### Loggers Externes

- **uvicorn** : Serveur web
- **fastapi** : Framework
- **sqlalchemy** : Base de données

## Fonctions Utilitaires

### Logging des Opérations Business

```python
from src.api.logging_config import log_business_operation

log_business_operation(
    logger=logger,
    operation="CREATE",
    entity="Store",
    entity_id="123",
    user="admin",
    store_name="Nouveau Magasin"
)
```

### Logging des Appels API

```python
from src.api.logging_config import log_api_call

log_api_call(
    logger=logger,
    method="POST",
    endpoint="/api/v1/stores",
    status_code=201,
    response_time=0.150,
    user="admin"
)
```

### Logging des Erreurs avec Contexte

```python
from src.api.logging_config import log_error_with_context

try:
    # Opération risquée
    pass
except Exception as e:
    log_error_with_context(
        logger=logger,
        error=e,
        context={
            "operation": "create_store",
            "store_id": store_id,
            "user": "admin"
        }
    )
```

## Formats de Logs

### Format Détaillé (Fichiers)

```
2024-01-01 10:30:45 - api.endpoints.stores - INFO - create_store:67 - Creating new store: Magasin Test
```

### Format Simple (Console)

```
2024-01-01 10:30:45 - INFO - Creating new store: Magasin Test
```

### Format JSON (Business)

```json
{
  "timestamp": "2024-01-01 10:30:45",
  "level": "INFO",
  "logger": "api.services.stores",
  "function": "create_store",
  "line": 67,
  "message": "Business Operation: CREATE on Store (ID: 123) - store_name=Magasin Test"
}
```

## Middleware de Logging

Le middleware automatique enregistre :

- **Requêtes entrantes** : Méthode, URL, timestamp
- **Réponses sortantes** : Code de statut, temps de traitement
- **Headers de performance** : `X-Process-Time`

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Logging automatique de toutes les requêtes
    pass
```

## Rotation des Logs

- **Taille maximum** : 10 MB par fichier
- **Fichiers de sauvegarde** : 5-10 selon le type
- **Rotation automatique** : Quand la taille limite est atteinte
- **Encodage** : UTF-8

## Utilisation en Développement

### Démarrage avec Logging

```bash
# Démarrer l'API avec logging activé
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Tester le logging
python test_logging.py

# Voir les logs en temps réel
tail -f src/logs/api_$(date +%Y-%m-%d).log
```

### Test du Système de Logging

```bash
# Exécuter les tests avec logging
python test_logging.py

# Voir le contenu des logs
python test_logging.py --logs

# Surveiller les erreurs
tail -f src/logs/errors_$(date +%Y-%m-%d).log
```

## Bonnes Pratiques

### Dans les Endpoints

```python
@router.post("/stores/", response_model=StoreResponse)
def create_store(store: StoreCreate, store_service: StoreService = Depends(get_store_service)):
    logger.info(f"Creating store: {store.nom}")
    
    try:
        result = store_service.create_store(store)
        log_business_operation(logger, "CREATE", "Store", str(result.id))
        return result
    except Exception as e:
        log_error_with_context(logger, e, {"operation": "create_store"})
        raise
```

### Dans les Services

```python
class StoreService:
    def __init__(self, repository):
        self.repository = repository
        self.logger = get_logger("api.services.stores")
    
    def create_store(self, store_data):
        self.logger.info(f"Creating store: {store_data.nom}")
        # Logique métier...
```

### Gestion des Erreurs

```python
try:
    # Opération
    pass
except ValueError as e:
    logger.warning(f"Business logic error: {e}")
    raise BusinessLogicError(str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## Monitoring et Alertes

### Surveillance des Logs

```bash
# Erreurs récentes
grep "ERROR" src/logs/api_$(date +%Y-%m-%d).log | tail -10

# Opérations business du jour
cat src/logs/business_$(date +%Y-%m-%d).log | jq '.'

# Performance des API
grep "API Call" src/logs/api_$(date +%Y-%m-%d).log | grep -E "\([0-9]+\.[0-9]+s\)"
```

### Métriques Importantes

- Temps de réponse des endpoints
- Taux d'erreur par endpoint
- Opérations business par type
- Authentification échouée

## Intégration avec les Tests

Les tests unitaires utilisent des loggers mockés pour éviter la pollution des logs :

```python
def test_create_store(client, mock_store_service):
    # Les logs sont automatiquement mockés
    response = client.post("/api/v1/stores/", json=store_data)
    assert response.status_code == 201
```

## Sécurité

- **Données sensibles** : Jamais loggées (mots de passe, tokens)
- **PII** : Informations personnelles minimisées
- **Rotation** : Suppression automatique des vieux logs
- **Accès** : Logs accessibles uniquement aux administrateurs

## Dépannage

### Problèmes Courants

1. **Répertoire logs manquant** : Créé automatiquement au démarrage
2. **Permissions** : Vérifier les droits d'écriture
3. **Espace disque** : Surveiller la taille des logs
4. **Performance** : Ajuster le niveau de logging en production

### Debug

```python
# Activer le debug temporairement
import logging
logging.getLogger("api").setLevel(logging.DEBUG)
```

## Exemple Complet

Voir le fichier `test_logging.py` pour un exemple complet d'utilisation du système de logging avec tous les types d'opérations. 