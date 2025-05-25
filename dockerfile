# syntax=docker/dockerfile:1
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src ./src

# Création du dossier de données
RUN mkdir -p /app/data

# Initialisation de la base de données
CMD ["sh", "-c", "exec python -m src.main"]
