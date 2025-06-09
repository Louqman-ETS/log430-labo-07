# syntax=docker/dockerfile:1
FROM python:3.9-slim

WORKDIR /app

# Ajouter le répertoire de travail au PYTHONPATH
ENV PYTHONPATH=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY src/ src/

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Flask
EXPOSE 8080

# Lancer l'application Flask directement
CMD ["python", "-m", "src.app.run"]
