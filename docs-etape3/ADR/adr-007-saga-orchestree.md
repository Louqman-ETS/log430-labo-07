# ADR-007 : Adoption du Pattern Saga Orchestrée

## Status
Accepté

## Context
Dans un environnement de microservices, nous devons maintenir la cohérence des transactions qui impliquent plusieurs services indépendants. Les transactions ACID traditionnelles ne sont pas applicables dans un contexte distribué où chaque service gère sa propre base de données.

### Problématiques identifiées :
- **Cohérence des données** : Comment s'assurer que toutes les opérations réussissent ou échouent ensemble
- **Gestion des pannes partielles** : Que faire quand certaines étapes réussissent et d'autres échouent  
- **Traçabilité** : Comment suivre l'état global d'une transaction distribuée
- **Récupération** : Comment annuler les opérations déjà effectuées en cas d'échec

### Options considérées :

1. **Two-Phase Commit (2PC)**
   - Non applicable : Nécessite un coordinateur de transaction global
   - Bloquant : Peut créer des deadlocks en cas de panne
   - Performance : Synchronisation coûteuse

2. **Saga Chorégraphiée**
   - Décentralisée : Pas de point de défaillance unique
   - Complexité : Logique de compensation distribuée
   - Debugging difficile : État global non visible
   - Évolutivité : Ajout d'étapes complexe

3. **Saga Orchestrée**
   - Contrôle centralisé : Logique de coordination simplifiée
   - Visibilité : État global traçable
   - Debugging facilité : Point central de coordination
   - Point de défaillance : Dépendance à l'orchestrateur

## Decision
Nous adoptons le **pattern Saga Orchestrée** pour gérer les transactions distribuées dans notre système de traitement de commandes.

### Justifications :

1. **Contrôle centralisé** : Un orchestrateur central (`saga-orchestrator-api`) coordonne l'ensemble du processus, facilitant la logique métier complexe

2. **Visibilité et traçabilité** : L'état global de chaque transaction est visible et persisté, permettant un monitoring et debugging efficaces

3. **Gestion d'erreurs simplifiée** : La logique de compensation est centralisée dans l'orchestrateur

4. **Évolutivité** : L'ajout de nouvelles étapes ou la modification du workflow est simplifié

5. **Observabilité** : Métriques et logs centralisés pour le monitoring

### Architecture retenue :

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Client API    │───▶│ Saga Orchestrator │◀──▶│  Services Métier │
└─────────────────┘    └──────────────────┘    │  - inventory-api │
                                │              │  - ecommerce-api │
                                ▼              │  - retail-api    │
                       ┌──────────────────┐    └──────────────────┘
                       │ Saga Database    │
                       │ (PostgreSQL)     │
                       └──────────────────┘
```

## Consequences

### Positives :
- **Meilleure traçabilité** : Historique complet des transactions avec états intermédiaires
- **Gestion centralisée des erreurs** : Logique de compensation dans un seul service
- **Facilité de monitoring** : Dashboard Grafana avec métriques Prometheus
- **Debugging simplifié** : Logs centralisés avec contexte complet
- **Évolutivité** : Ajout facile de nouvelles étapes dans le workflow

### Négatives :
- **Point de défaillance unique** : L'orchestrateur devient critique
- **Couplage plus fort** : Les services doivent exposer des APIs pour l'orchestrateur
- **Complexité opérationnelle** : Service supplémentaire à maintenir et monitorer

### Mesures d'atténuation :
1. **Haute disponibilité** : Déploiement multi-instance de l'orchestrateur avec load balancing
2. **Monitoring renforcé** : Alertes sur la santé de l'orchestrateur
3. **Circuit breakers** : Protection contre les pannes en cascade
4. **Retry policies** : Gestion automatique des erreurs transitoires

## Implémentation

### Services impliqués :
- **saga-orchestrator-api** : Orchestrateur central
- **inventory-api** : Gestion du stock
- **ecommerce-api** : Gestion des commandes et clients

### Workflow de traitement de commande :
1. `CHECK_STOCK` → Vérification disponibilité
2. `RESERVE_STOCK` → Réservation temporaire  
3. `CREATE_ORDER` → Création commande
4. `PROCESS_PAYMENT` → Traitement paiement
5. `CONFIRM_ORDER` → Finalisation

### Mécanismes de compensation :
- `RELEASE_STOCK` ← `RESERVE_STOCK`
- `CANCEL_ORDER` ← `CREATE_ORDER`  
- `REFUND_PAYMENT` ← `PROCESS_PAYMENT`

## Révision
Cette décision sera réévaluée si :
- Les performances de l'orchestrateur deviennent un goulot d'étranglement
- La complexité opérationnelle devient excessive
- De nouveaux patterns émergent qui résolvent mieux nos problématiques 