# syntax=docker/dockerfile:1
FROM python:3.9-slim

WORKDIR /app

# Ajouter le répertoire de travail au PYTHONPATH
ENV PYTHONPATH=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY src/ src/
COPY entrypoint.sh .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Rendre le script d'entrée exécutable
RUN chmod +x entrypoint.sh

# Définir le script d'entrée
ENTRYPOINT ["./entrypoint.sh"]
