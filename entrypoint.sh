#!/bin/bash

# Attendre que la base de données soit prête
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Lancer l'application
echo "Starting application..."
exec python -m src.main 