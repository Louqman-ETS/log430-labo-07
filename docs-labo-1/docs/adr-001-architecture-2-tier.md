# ADR 001: Architecture 2-Tier avec PostgreSQL

## Statut

Accepté

## Contexte

Le système de caisse de magasin nécessite une architecture qui permet :
- La gestion des données de manière persistante et fiable
- Une séparation claire entre la logique métier et le stockage des données
- Une possibilité de déploiement distribué
- Une maintenance et une évolution facile du système

## Décision

Nous avons choisi d'implémenter une architecture 2-tier avec :
- Un client Python en console pour l'interface utilisateur et la logique métier
- Un serveur PostgreSQL pour la persistance des données

## Conséquences

### Avantages
- Séparation claire des responsabilités
- PostgreSQL offre des fonctionnalités avancées (transactions, contraintes, etc.)
- Facilité de déploiement avec Docker
- Permet de gérer la concurrence des donnés
- Support robuste des transactions concurrentes

### Inconvénients
- Dépendance à PostgreSQL
- Nécessité de gérer la connexion réseau entre le client et le serveur
- Configuration initiale plus complexe qu'une solution fichier
- Besoin de gérer les migrations de base de données

## Notes
- Version de PostgreSQL minimale requise : 13+
- La connexion est gérée via SQLAlchemy pour l'abstraction
- Les paramètres de connexion sont configurables via variables d'environnement 