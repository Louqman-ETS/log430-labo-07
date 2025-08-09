# ADR-011 – Choix de Redis Streams comme bus d’événements

## Contexte
Besoin d’un bus léger pour un labo, déjà présent dans l’écosystème du projet, supportant groupes de consommateurs et relecture.

## Décision
Utiliser Redis Streams pour Pub/Sub avec persistance (XADD, XREADGROUP), groupes, idempotence simple, et faible friction d’opération.

## Alternatives
- Kafka: très robuste mais plus complexe à opérer (cluster, ZooKeeper non requis mais infra plus lourde).
- RabbitMQ: excellent pour files, moins orienté stream/replay.

## Conséquences
- + Simplicité d’intégration, learning curve faible, relecture possible.
- − Moins adapté aux charges massives qu’un Kafka en prod.


