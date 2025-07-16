# ADR-005: Kong Gateway pour Load Balancing

## Statut
Accepté

## Contexte
L'architecture microservices nécessite un point d'entrée unique pour gérer le trafic vers les différents services. Le service Inventory API doit être répliqué en 3 instances pour supporter la charge et assurer la haute disponibilité. Nous devons choisir une solution de load balancing et d'API Gateway.

## Décision
Nous adoptons Kong Gateway comme solution unique pour :
- API Gateway (point d'entrée unique)
- Load Balancer (répartition de charge)
- Service Discovery (découverte automatique des instances)
- Rate Limiting (limitation du trafic)

### Configuration retenue
- **Kong Gateway** : 1 instance centrale
- **Inventory API** : 3 instances load balancées par Kong
- **Autres APIs** : 1 instance chacune, routées via Kong
- **Communication** : HTTP/REST via Kong uniquement

## Alternatives considérées

### 1. Nginx Load Balancer
- **Avantages** : Simple, performant
- **Inconvénients** : Configuration manuelle, pas de gestion API
- **Rejet** : Trop basique pour une architecture microservices

### 2. HAProxy + API Gateway séparé
- **Avantages** : Très performant pour le load balancing
- **Inconvénients** : Complexité de gestion de 2 composants
- **Rejet** : Architecture plus complexe

### 3. Service Mesh (Istio)
- **Avantages** : Fonctionnalités avancées
- **Inconvénients** : Complexité excessive pour notre contexte
- **Rejet** : Over-engineering

## Conséquences

### Positives
- **Point d'entrée unique** : Simplification du routage client
- **Load balancing intégré** : Répartition automatique vers les 3 instances Inventory
- **Gestion centralisée** : Configuration déclarative via kong-loadbalanced.yml
- **Monitoring intégré** : Métriques Prometheus natives
- **Scalabilité** : Ajout facile de nouvelles instances

### Négatives
- **Point de défaillance** : Kong devient critique
- **Courbe d'apprentissage** : Configuration Kong plus complexe que Nginx
- **Performance** : Légère latence ajoutée par rapport à l'accès direct

## Notes d'implémentation
- Configuration déclarative dans `kong/kong-loadbalanced.yml`
- Health checks automatiques des instances Inventory
- Métriques exportées vers Prometheus
- Tests de charge validés avec k6 (100 utilisateurs simultanés)

## Métriques de succès
- 100 utilisateurs simultanés supportés sans erreur
- Latence p95 < 105ms maintenue
- Taux d'erreur < 1%
- Load balancing équilibré entre les 3 instances

## Date
2024-12-05

## Participants
- Équipe Architecture
- Équipe DevOps
- Équipe Développement 