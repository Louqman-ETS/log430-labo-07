# Makefile pour l'écosystème de microservices LOG430
.PHONY: help build start stop clean logs test

# Couleurs pour l'affichage
CYAN=\033[0;36m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## 📋 Afficher l'aide
	@echo "$(CYAN)🛒 Écosystème E-Commerce - Microservices$(NC)"
	@echo ""
	@echo "$(GREEN)Services Magasin (Fusionnés):$(NC)"
	@echo "  • Inventory API (8001) - Gestion produits, catégories & stocks"
	@echo "  • Retail API (8002) - Gestion magasins, caisses & ventes"
	@echo "  • Reporting API (8005) - Rapports & analytics"
	@echo ""
	@echo "$(YELLOW)Services E-Commerce (Unifiés):$(NC)"
	@echo "  • Ecommerce API (8000) - Clients, paniers & commandes"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ================================
# SERVICES MAGASIN (EXISTANTS)
# ================================

build-store: ## 🏗️ Construire tous les services magasin
	@echo "$(CYAN)🏗️ Construction des services magasin...$(NC)"
	docker-compose -f docker-compose.yml build

start-store: ## 🚀 Démarrer tous les services magasin
	@echo "$(GREEN)🚀 Démarrage des services magasin...$(NC)"
	docker-compose -f docker-compose.yml up -d
	@echo "$(GREEN)✅ Services magasin démarrés!$(NC)"
	@echo "📊 Dashboards disponibles:"
	@echo "  • Grafana: http://localhost:3000"
	@echo "  • Prometheus: http://localhost:9090"

stop-store: ## 🛑 Arrêter tous les services magasin
	@echo "$(YELLOW)🛑 Arrêt des services magasin...$(NC)"
	docker-compose -f docker-compose.yml down

# ================================
# SERVICES E-COMMERCE (NOUVEAUX)
# ================================

build-ecommerce: ## 🛒 Construire tous les services e-commerce
	@echo "$(CYAN)🛒 Construction des services e-commerce...$(NC)"
	docker-compose -f docker-compose.ecommerce.yml build

start-ecommerce: ## 🚀 Démarrer le service e-commerce
	@echo "$(GREEN)🚀 Démarrage du service e-commerce...$(NC)"
	cd services && docker-compose up -d ecommerce-api
	@echo "$(GREEN)✅ Service e-commerce démarré!$(NC)"
	@echo "🛒 API disponible:"
	@echo "  • Ecommerce API: http://localhost:8000"

stop-ecommerce: ## 🛑 Arrêter le service e-commerce
	@echo "$(YELLOW)🛑 Arrêt du service e-commerce...$(NC)"
	cd services && docker-compose stop ecommerce-api

# ================================
# COMMANDES GLOBALES
# ================================

build: build-store build-ecommerce ## 🏗️ Construire TOUS les services

start: start-store start-ecommerce ## 🚀 Démarrer TOUS les services
	@echo ""
	@echo "$(GREEN)🎉 ÉCOSYSTÈME COMPLET DÉMARRÉ!$(NC)"
	@echo ""
	@echo "$(CYAN)🏪 Services Magasin:$(NC)"
	@echo "  • Inventory API: http://localhost:8001"
	@echo "  • Retail API: http://localhost:8002"
	@echo "  • Reporting API: http://localhost:8005"
	@echo ""
	@echo "$(YELLOW)🛒 Services E-Commerce:$(NC)"
	@echo "  • Ecommerce API: http://localhost:8000"

stop: stop-store stop-ecommerce ## 🛑 Arrêter TOUS les services

restart: stop start ## 🔄 Redémarrer TOUS les services

# ================================
# LOGS ET MONITORING
# ================================

logs-store: ## 📜 Voir les logs des services magasin
	docker-compose -f docker-compose.yml logs -f

logs-ecommerce: ## 📜 Voir les logs du service e-commerce
	cd services && docker-compose logs -f ecommerce-api

logs: ## 📜 Voir TOUS les logs
	@echo "$(CYAN)📜 Logs des services magasin:$(NC)"
	docker-compose -f docker-compose.yml logs --tail=50
	@echo ""
	@echo "$(YELLOW)📜 Logs du service e-commerce:$(NC)"
	cd services && docker-compose logs --tail=50 ecommerce-api

status: ## 📊 Vérifier le statut de tous les services
	@echo "$(CYAN)📊 Statut des services:$(NC)"
	@echo ""
	@echo "$(GREEN)🏪 Services Magasin:$(NC)"
	@docker-compose -f docker-compose.yml ps
	@echo ""
	@echo "$(YELLOW)🛒 Services E-Commerce:$(NC)"
	@cd services && docker-compose ps ecommerce-api

# ================================
# TESTS
# ================================

test-store: ## 🧪 Exécuter les tests des services magasin
	@echo "$(CYAN)🧪 Tests des services magasin...$(NC)"
	cd services && python run_all_tests.py

test-ecommerce: ## 🧪 Exécuter les tests du service e-commerce
	@echo "$(CYAN)🧪 Tests du service e-commerce...$(NC)"
	cd services/ecommerce-api && python -m pytest tests/ -v

test: test-store test-ecommerce ## 🧪 Exécuter TOUS les tests

# ================================
# INITIALISATION ET NETTOYAGE
# ================================

init-data: ## 📊 Initialiser les données de test
	@echo "$(CYAN)📊 Initialisation des données de test...$(NC)"
	@echo "🏪 Initialisation services magasin..."
	cd services/inventory-api/src && python init_db.py
	cd services/retail-api/src && python init_db.py
	@echo "🛒 Initialisation service e-commerce..."
	cd services/ecommerce-api/src && python init_db.py
	@echo "$(GREEN)✅ Données de test initialisées!$(NC)"

clean: ## 🧹 Nettoyer les containers et volumes
	@echo "$(RED)🧹 Nettoyage des containers et volumes...$(NC)"
	docker-compose -f docker-compose.yml down -v
	cd services && docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✅ Nettoyage terminé!$(NC)"

# ================================
# DÉVELOPPEMENT
# ================================

dev-ecommerce: ## 🔧 Mode développement Ecommerce API
	cd services/ecommerce-api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# ================================
# LINTING ET FORMATAGE
# ================================

format: ## 🎨 Formater le code avec black
	@echo "$(CYAN)🎨 Formatage du code avec black...$(NC)"
	python -m black --line-length 88 .
	@echo "$(GREEN)✅ Code formaté!$(NC)"

check-format: ## 🔎 Vérifier le formatage sans modification
	@echo "$(CYAN)🔎 Vérification du formatage...$(NC)"
	python -m black --check --line-length 88 .
	@echo "$(GREEN)✅ Formatage vérifié!$(NC)"

# ================================
# DOCUMENTATION
# ================================

docs: ## 📚 Ouvrir la documentation des APIs
	@echo "$(CYAN)📚 Documentation des APIs:$(NC)"
	@echo "🏪 Services Magasin:"
	@echo "  • Inventory API: http://localhost:8001/docs"
	@echo "  • Retail API: http://localhost:8002/docs"
	@echo "  • Reporting API: http://localhost:8005/docs"
	@echo ""
	@echo "🛒 Services E-Commerce:"
	@echo "  • Ecommerce API: http://localhost:8000/docs" 