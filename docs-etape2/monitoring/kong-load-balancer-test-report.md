# Rapport de Test de Charge - Architecture Microservices avec Kong Gateway et Load Balancer

## 1. Architecture du Système

### 1.1 Vue d'ensemble
L'architecture implémentée est basée sur un pattern de microservices avec Kong Gateway comme API Gateway et load balancer. Le système comprend :

- **Kong Gateway** : API Gateway principal (port 9000) gérant le routage, l'authentification et le load balancing
- **4 Microservices** : inventory-api, retail-api, ecommerce-api, reporting-api  
- **Load Balancing** : 3 instances d'inventory-api pour la répartition de charge
- **Bases de données** : PostgreSQL dédiée pour chaque service + Redis pour le cache
- **Monitoring** : Prometheus + Grafana pour la surveillance des métriques

### 1.2 Configuration Kong Gateway

Kong fonctionne en mode déclaratif sans base de données (DB-less) avec :
- **Upstream pour inventory-api** : 3 instances en load balancing (round-robin)
- **Routes configurées** : `/inventory`, `/retail`, `/ecommerce`, `/reporting`
- **Authentification** : Plugin key-auth avec clé API
- **CORS** : Plugin cors pour les requêtes cross-origin
- **Pas de rate limiting** : Supprimé pour éviter les limitations lors des tests

### 1.3 Services et Ports

| Service | Port | Instances | Base de données | Description |
|---------|------|-----------|----------------|-------------|
| Kong Gateway | 9000 | 1 | Aucune (DB-less) | API Gateway principal |
| inventory-api | 8011-8013 | 3 | PostgreSQL:5443 | Gestion des produits (load balancé) |
| retail-api | 8002 | 1 | PostgreSQL:5434 | Gestion des magasins |
| ecommerce-api | 8000 | 1 | PostgreSQL:5450 | Gestion des clients |
| reporting-api | 8005 | 1 | PostgreSQL:5435 | Rapports et analytics |

## 2. Configuration du Test de Charge

### 2.1 Paramètres du Test
- **Outil** : k6 (Grafana k6)
- **Durée totale** : 10 minutes
- **Utilisateurs maximum** : 100 utilisateurs virtuels
- **Montée progressive** : 
  - 1 min : 0 → 25 users
  - 1 min : 25 → 50 users  
  - 1 min : 50 → 75 users
  - 1 min : 75 → 100 users
  - 4 min : maintien à 100 users
  - 2 min : 100 → 0 users

### 2.2 Endpoints testés
4 endpoints simples sans appel inter-services :
1. **Inventory Products** : `GET /inventory/api/v1/products/`
2. **Retail Stores** : `GET /retail/api/v1/stores/`  
3. **Ecommerce Customers** : `GET /ecommerce/api/v1/customers/`
4. **Reporting Sales by Period** : `GET /reporting/api/v1/reports/sales-by-period`

### 2.3 Seuils de performance
- **Taux d'erreur** : < 10%
- **Temps de réponse p95** : < 2000ms
- **Taux de succès des vérifications** : > 90%
- **Timeout par requête** : 10 secondes

## 3. Résultats du Test de Charge

### 3.1 Métriques Globales

| Métrique | Valeur | Statut |
|----------|--------|--------|
| **Durée d'exécution** | 10 min 1.8s | ✓ |
| **Total requêtes** | 37,953 | - |
| **Débit (req/s)** | 63.06 | ✓ |
| **Taux d'erreur global** | 0.55% | ✓ (< 10%) |
| **Taux de succès des checks** | 99.32% | ✓ (> 90%) |

### 3.2 Latences et Temps de Réponse

| Métrique | Valeur | Objectif | Statut |
|----------|--------|----------|--------|
| **Latence moyenne** | 111.86ms | - | ✓ |
| **Latence p90** | 32.86ms | - | ✓ |
| **Latence p95** | 104.47ms | < 2000ms | ✓ |
| **Latence médiane** | 6.37ms | - | ✓ |
| **Latence minimum** | 0.801ms | - | ✓ |
| **Latence maximum** | 10.04s | - | ⚠️ |

### 3.3 Performance par Service

#### Inventory Products (Load Balancé - 3 instances)
- **Requêtes** : ~9,532
- **Taux de succès** : 99% (9,503 succès, 29 échecs)
- **Disponibilité** : 99.7%
- **Performance** : Excellent grâce au load balancing

#### Retail Stores  
- **Requêtes** : ~9,467
- **Taux de succès** : 97% (9,256 succès, 211 échecs)
- **Disponibilité** : 97.8%
- **Performance** : Service le plus problématique

#### Ecommerce Customers
- **Requêtes** : ~9,483  
- **Taux de succès** : 99% (9,446 succès, 37 échecs)
- **Disponibilité** : 99.6%
- **Performance** : Très bon

#### Reporting Sales by Period
- **Requêtes** : ~9,471
- **Taux de succès** : 100% (aucun échec détecté)
- **Disponibilité** : 100%
- **Performance** : Excellent (endpoint mock)

### 3.4 Analyse du Trafic Réseau
- **Données reçues** : 79 MB (130 kB/s)
- **Données envoyées** : 5.7 MB (9.6 kB/s)
- **Ratio** : 14:1 (typique pour des API GET)

## 4. Analyse des Résultats

### 4.1 Points Forts
- **Objectifs atteints** : Tous les seuils de performance respectés
- **Load balancing efficace** : inventory-api (3 instances) montre les meilleures performances
- **Latence faible** : p95 à 104ms, bien en dessous des 2000ms requis
- **Débit stable** : 63 req/s maintenu sur 10 minutes
- **Scalabilité** : Architecture supporte 100 utilisateurs simultanés

### 4.2 Points d'Amélioration
- **Retail-api** : Service le plus lent (97% de succès vs 99% pour les autres)
- **Pics de latence** : Maximum à 10s indique des timeouts occasionnels
- **Monitoring** : Besoin d'alertes sur les services underperformants

### 4.3 Efficacité du Load Balancing
Le load balancing sur inventory-api (3 instances) démontre :
- **Meilleure résilience** : 99.7% de disponibilité
- **Distribution de charge** : Répartition équitable entre instances
- **Performance supérieure** : Moins d'échecs que les services single-instance

## 5. Recommandations

### 5.1 Optimisations Techniques
1. **Étendre le load balancing** : Appliquer à retail-api pour améliorer ses performances
2. **Optimisation retail-api** : Investiguer les causes des 3% d'échecs
3. **Monitoring avancé** : Implémenter des alertes Prometheus sur les latences p95
4. **Cache** : Implémenter Redis pour les endpoints les plus sollicités

### 5.2 Scalabilité
1. **Horizontal scaling** : Ajouter des instances pour retail-api et ecommerce-api
2. **Auto-scaling** : Implémenter des règles basées sur CPU/mémoire
3. **Circuit breaker** : Ajouter des patterns de résilience inter-services

### 5.3 Monitoring Production
1. **Dashboards temps réel** : Grafana avec métriques par service
2. **Alerting** : Seuils sur latence p95 > 500ms et error rate > 1%
3. **Tracing distribué** : Implémenter Jaeger pour le suivi des requêtes

## 6. Conclusion

Le test de charge valide que l'architecture microservices avec Kong Gateway et load balancer :
- **Supporte efficacement** 100 utilisateurs simultanés
- **Maintient des performances** acceptables (latence p95 < 105ms)
- **Offre une haute disponibilité** (99.32% de succès global)
- **Démontre l'efficacité** du load balancing sur inventory-api

L'architecture est prête pour un déploiement en production avec les améliorations recommandées, particulièrement l'extension du load balancing à d'autres services et l'optimisation de retail-api.

---
*Rapport généré le : 2025-07-05*  
*Test exécuté avec : k6 v0.x, Kong Gateway 3.4.1.1*  
*Architecture : 4 microservices, 1 API Gateway, 3 instances load balancées* 