# ADR-010 – Saga chorégraphiée pour le checkout e‑commerce

## Contexte
Le checkout implique plusieurs services (commande, stock, paiement). Besoin d’atomicité logique distribuée et de résilience.

## Décision
Implémenter une saga chorégraphiée (basée événements) plutôt qu’un orchestrateur central. Les services réagissent aux événements (`OrderCreated`, `PaymentFailed`, …). `inventory-saga-consumer` gère la réservation/compensation du stock.

## Alternatives
- Orchestrateur (ex. `saga-orchestrator-api`) : plus centralisé, plus de couplage, plus de code de coordination.
- Transactions distribuées 2PC : complexité, verrouillage, peu adapté microservices.

## Conséquences
- + Découplage, scalabilité, tolérance aux pannes.
- − Visibilité/traçage plus complexe (nécessite un Event Store/observabilité).


