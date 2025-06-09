# ADR 002: Utilisation de SQLAlchemy comme ORM

## Statut

Accepté

## Contexte

Le projet nécessite une interface efficace et sécurisée pour interagir avec la base de données PostgreSQL. Les besoins principaux sont :
- Une abstraction de la base de données
- Une gestion efficace des connexions
- Un mapping objet-relationnel robuste

## Décision

Nous avons choisi d'utiliser SQLAlchemy 2.0+ comme ORM (Object-Relational Mapping) pour les raisons suivantes :
- Maturité et stabilité du projet
- Large adoption dans la communauté Python
- Support complet des fonctionnalités PostgreSQL

## Conséquences

### Avantages
- Code plus maintenable avec des modèles Python
- Protection automatique contre les injections SQL
- Gestion automatique du pool de connexions
- Facilité de test avec les sessions de test

### Inconvénients
- Légère surcharge de performance par rapport au SQL brut
- Complexité accrue pour les requêtes très complexes
- Dépendance supplémentaire dans le projet

## Notes
- Version utilisée : SQLAlchemy 2.0.23
- Configuration du pool : POOL_SIZE=5, MAX_OVERFLOW=10
- Utilisation de l'API moderne avec les types Python
- Integration avec psycopg2-binary comme driver PostgreSQL 