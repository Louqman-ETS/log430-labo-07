# log430-labo-0

# Build + run
docker compose up --build

# Ou, pour exécuter en arrière‑plan :
docker compose up -d

# Voir les logs en streaming
docker compose logs -f hello

# Arrêt + suppression du conteneur
docker compose down