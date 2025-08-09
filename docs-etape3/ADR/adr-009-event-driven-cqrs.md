# ADR-009: Architecture événementielle avec CQRS et Event Store

- Scénario retenu: « Panier e-commerce » (création, ajout d’articles, checkout, expiration future).
- Événements clés: `CartCreated`, `CartItemAdded`, `CartCheckedOut`, `OrderCreated`.
- Bus d’événements: Redis Streams.
- Event Store: PostgreSQL dédié.
- Consommateurs: `event-audit-api` (persistance, replay), `event-notifier` (notifications).
- CQRS: write = `ecommerce-api`, read = projections via `event-audit-api`.

Justification: Redis existe déjà, mise en place rapide, suffisante pour le labo. Kafka/RabbitMQ plus lourds à opérer.

Idempotence & Résilience:
- Groupes de consommateurs Redis avec ACK.
- `event-audit-api` stocke par `message_id` pour éviter les doublons.
- `event-notifier` utilise une clé Redis éphémère pour dédupliquer.
- Si Redis indisponible, l’éditeur se désactive proprement et l’API continue.
