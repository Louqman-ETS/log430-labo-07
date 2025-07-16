# ADR-008 : Gestion des Customer ID dans les URLs

## Status
Accepté

## Context
L'API initiale de traitement de commandes (`/order-processing`) créait automatiquement des customers quand l'ID fourni dans le payload n'existait pas dans le système. Ce comportement posait plusieurs problèmes :

### Problématiques identifiées :

1. **Comportement imprévisible** : L'API pouvait silencieusement créer des entities au lieu de retourner une erreur
2. **Design API non-RESTful** : L'ID du customer était dans le body au lieu de l'URL
3. **Logique métier incohérente** : Un service de traitement de commandes ne devrait pas créer de customers
4. **Sécurité** : Risque de création non intentionnelle de données

### Comportement problématique observé :

L'ancien endpoint acceptait des requests avec un customer_id inexistant dans le payload JSON, créait automatiquement un nouveau customer avec un ID différent de celui demandé, masquant ainsi l'erreur logique.

### Options considérées :

1. **Maintenir le comportement actuel**
   - Imprévisible : Comportement magique non documenté
   - Non-RESTful : ID dans le body au lieu de l'URL
   - Sécurité : Création silencieuse de données

2. **Validation stricte avec endpoint RESTful**
   - Prévisible : Erreur explicite si customer inexistant
   - RESTful : ID dans l'URL comme ressource parent
   - Séparation des responsabilités : Pas de création de customer

3. **Validation avec fallback optionnel**
   - Complexe : Paramètre pour activer/désactiver la création
   - Ambiguïté : Comportement variable selon le contexte

## Decision
Nous adoptons la **validation stricte avec endpoint RESTful** :

### Nouveau design d'API :

L'ancien endpoint utilisait un POST sur `/order-processing` avec le customer_id dans le payload JSON.

Le nouveau endpoint utilise un design RESTful avec `/customers/{customer_id}/order-processing` où l'ID du customer est extrait de l'URL, et le payload ne contient plus que les informations de la commande (produits, adresses, méthode de paiement).

### Justifications :

1. **Design RESTful** : L'ID du customer devient une ressource parent dans l'URL
2. **Validation explicite** : Vérification de l'existence du customer avant traitement
3. **Séparation des responsabilités** : Le service saga n'est plus responsable de la création de customers
4. **Prédictibilité** : Erreur claire et explicite si le customer n'existe pas

## Implementation

### Validation du Customer ID :

La validation du customer est effectuée par un appel GET à l'API ecommerce pour vérifier l'existence du customer avant de procéder à la création de la commande. Si le customer n'existe pas, une exception est levée avec un message explicite.

### Nouveau schéma de requête :

Le nouveau schéma de requête ne contient plus le customer_id dans le payload JSON. Il inclut uniquement les informations de commande : liste des produits, adresses de livraison et facturation, et méthode de paiement. Le customer_id est maintenant extrait de l'URL.

### Nouvelle route API :

La nouvelle route API utilise le pattern RESTful `/customers/{customer_id}/order-processing` où le customer_id est un paramètre de chemin. La fonction extrait l'ID du customer de l'URL, combine les données de la requête avec cet ID, et démarre la saga de traitement de commande.

## Consequences

### Positives :
- **Comportement prévisible** : Erreur explicite si customer inexistant
- **API RESTful** : Respecte les conventions REST avec ressources hiérarchiques
- **Validation métier appropriée** : Vérification des prérequis avant traitement
- **Sécurité renforcée** : Pas de création silencieuse de données
- **Debugging facilité** : Messages d'erreur clairs et explicites
- **Cohérence** : Uniformité avec les autres APIs du système

### Négatives :
- **Étape supplémentaire** : Nécessite la création préalable des customers
- **Appel réseau supplémentaire** : Vérification de l'existence du customer
- **Breaking change** : Incompatible avec l'ancienne API

### Impacts sur les clients :

**Avant** (comportement magique) : L'ancien endpoint créait silencieusement un customer avec un ID différent de celui demandé, menant à une saga réussie avec des données incohérentes.

**Après** (comportement explicite) : Le nouveau endpoint retourne une erreur explicite si le customer n'existe pas, causant l'échec de la saga qui est ensuite compensée automatiquement.

## Migration

### Phase 1 : Déploiement dual
- Maintenir l'ancien endpoint en mode dépréciée
- Ajouter le nouveau endpoint avec validation stricte
- Documenter la migration dans l'API

### Phase 2 : Migration des clients
- Mettre à jour les clients pour utiliser le nouveau endpoint
- Créer les customers manquants si nécessaire
- Tests de régression sur les nouveaux flows

### Phase 3 : Suppression de l'ancien endpoint
- Supprimer l'ancien endpoint `/order-processing`
- Nettoyer le code de création automatique de customers

## Monitoring
- **Métriques** : Taux d'erreur "Customer not found"
- **Alertes** : Pic d'erreurs lors de la migration
- **Logs** : Traçabilité des tentatives avec customers inexistants

## Révision
Cette décision sera réévaluée si :
- Le taux d'erreur "Customer not found" devient trop élevé
- Les performances de validation deviennent problématiques
- De nouveaux besoins métier émergent nécessitant la création automatique 