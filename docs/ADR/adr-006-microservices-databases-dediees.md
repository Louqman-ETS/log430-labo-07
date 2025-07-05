# ADR-006: Bases de Données Dédiées par Microservice

## Statut
Accepté

## Contexte
L'évolution depuis une API monolithique vers une architecture microservices nécessite de repenser la gestion des données. Nous devons décider entre maintenir une base de données partagée ou adopter des bases de données dédiées par service.

## Décision
Nous adoptons le pattern "Database per Service" avec des bases de données PostgreSQL dédiées pour chaque microservice :

### Architecture retenue
- **Inventory API** : `inventory_db` (Port 5433)
- **Ecommerce API** : `ecommerce_db` (Port 5450) 
- **Retail API** : `retail_db` (Port 5434)
- **Reporting API** : `reporting_db` (Port 5435)

### Principes appliqués
- **Isolation des données** : Chaque service contrôle ses propres données
- **Communication via API** : Aucun accès SQL direct entre services
- **Agrégation** : Reporting API collecte les données via REST calls

## Alternatives considérées

### 1. Base de données partagée
- **Avantages** : Simplicité, transactions ACID, pas de duplication
- **Inconvénients** : Couplage fort, scaling difficile, point de défaillance
- **Rejet** : Contraire aux principes microservices

### 2. Event Sourcing + CQRS
- **Avantages** : Découplage total, auditabilité
- **Inconvénients** : Complexité élevée, courbe d'apprentissage
- **Rejet** : Over-engineering pour notre contexte

### 3. Base partagée avec vues dédiées
- **Avantages** : Compromis entre isolation et simplicité
- **Inconvénients** : Couplage du schéma, évolution difficile
- **Rejet** : Fausse isolation

## Conséquences

### Positives
- **Autonomie des équipes** : Chaque service évolue indépendamment
- **Scalabilité** : Optimisation par service (index, tuning spécifique)
- **Résilience** : Panne d'une DB n'affecte qu'un service
- **Technologies** : Possibilité d'utiliser différents SGBD par service
- **Déploiement** : Migrations indépendantes par service

### Négatives
- **Complexité** : 4 bases de données à gérer
- **Cohérence** : Pas de transactions distribuées ACID
- **Duplication** : Certaines données référentielles dupliquées
- **Latence** : Communication inter-services via HTTP
- **Debugging** : Plus complexe de joindre les données

## Stratégies de gestion

### Communication inter-services
```
Ecommerce API → Kong → Inventory API (pour validation produits)
Retail API → Kong → Inventory API (pour réduction stock)  
Reporting API → Kong → Tous les APIs (pour agrégation)
```

### Gestion de la cohérence
- **Cohérence éventuelle** : Acceptable pour la plupart des cas
- **Validation en temps réel** : Pour les stocks critiques
- **Rollback manuel** : Processus de compensation en cas d'erreur

### Données de référence
- **Produits** : Source de vérité dans Inventory API
- **Clients** : Gérés dans Ecommerce API
- **Magasins** : Gérés dans Retail API
- **Rapports** : Agrégation dans Reporting API

## Notes d'implémentation
- PostgreSQL pour tous les services (cohérence opérationnelle)
- FastAPI + SQLAlchemy pour l'accès aux données
- Pas de foreign keys entre bases de données
- Validation des références via API calls
- Monitoring des performances de communication inter-services

## Métriques de succès
- Déploiements indépendants par service
- Temps de réponse < 200ms pour les API calls inter-services
- Disponibilité > 99.9% par service
- Isolation des pannes validée

## Risques identifiés
- **Cohérence des données** : Mitigation par validation temps réel
- **Performance** : Mitigation par cache et optimisation des requêtes
- **Complexité opérationnelle** : Mitigation par Docker Compose et monitoring

## Date
2024-12-05

## Participants
- Équipe Architecture
- Équipe Base de Données  
- Équipe Développement
- Product Owner 