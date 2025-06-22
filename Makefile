# Makefile pour LOG430-Labo-03
.PHONY: help build up down restart logs clean test

# Variables
COMPOSE_FILE=docker-compose.yml
PROJECT_NAME=log430-labo-03

# Couleurs pour l'affichage
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Afficher l'aide
	@echo "$(GREEN)LOG430-Labo-03 - Commandes Docker Compose$(NC)"
	@echo ""
	@echo "$(YELLOW)Commandes disponibles:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Construire les images Docker
	@echo "$(GREEN)Construction des images Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Démarrer tous les services
	@echo "$(GREEN)Démarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services démarrés!$(NC)"
	@echo "$(YELLOW)Web App:$(NC) http://localhost:8080"
	@echo "$(YELLOW)API:$(NC) http://localhost:8000"
	@echo "$(YELLOW)API Docs:$(NC) http://localhost:8000/docs"

up-dev: ## Démarrer en mode développement
	@echo "$(GREEN)Démarrage en mode développement...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up --build

down: ## Arrêter tous les services
	@echo "$(RED)Arrêt des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: down up ## Redémarrer tous les services

logs: ## Voir les logs de tous les services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Voir les logs de l'API
	docker-compose -f $(COMPOSE_FILE) logs -f api

logs-web: ## Voir les logs de l'app web
	docker-compose -f $(COMPOSE_FILE) logs -f web

status: ## Voir le statut des services
	@echo "$(GREEN)Statut des services:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

clean: ## Nettoyer les containers
	@echo "$(RED)Nettoyage des containers...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f

clean-all: ## Nettoyage complet (images, containers)
	@echo "$(RED)Nettoyage complet...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans --rmi all
	docker system prune -af

test: ## Exécuter les tests
	@echo "$(GREEN)Exécution des tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec api python -m pytest tests/ -v

shell-api: ## Ouvrir un shell dans le container API
	docker-compose -f $(COMPOSE_FILE) exec api /bin/bash

shell-web: ## Ouvrir un shell dans le container Web
	docker-compose -f $(COMPOSE_FILE) exec web /bin/bash

init: ## Initialiser le projet (première utilisation)
	@echo "$(GREEN)Initialisation du projet...$(NC)"
	@mkdir -p logs
	@echo "$(YELLOW)Créez un fichier .env basé sur .env.example$(NC)"
	@echo "$(GREEN)Projet initialisé! Utilisez 'make up' pour démarrer.$(NC)"

# Commande par défaut
.DEFAULT_GOAL := help 