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
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Installation des dépendances Python et création des répertoires nécessaires
RUN pip install --no-cache-dir -r requirements.txt && mkdir -p /var/log/supervisor

# Exposer les ports Flask et FastAPI
EXPOSE 8080
EXPOSE 8000

# Lancer supervisor
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
