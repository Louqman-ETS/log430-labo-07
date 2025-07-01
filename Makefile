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
	@echo "$(GREEN)Services Magasin (Existants):$(NC)"
	@echo "  • Products API (8001) - Gestion produits & catégories"
	@echo "  • Stores API (8002) - Gestion magasins & caisses"
	@echo "  • Sales API (8003) - Gestion ventes & ligne de ventes"
	@echo "  • Stock API (8004) - Gestion stocks & inventaires"
	@echo "  • Reporting API (8005) - Rapports & analytics"
	@echo ""
	@echo "$(YELLOW)Services E-Commerce (Nouveaux):$(NC)"
	@echo "  • Customers API (8006) - Comptes clients & authentification"
	@echo "  • Cart API (8007) - Paniers d'achat"
	@echo "  • Orders API (8008) - Commandes & checkout"
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

start-ecommerce: ## 🚀 Démarrer tous les services e-commerce
	@echo "$(GREEN)🚀 Démarrage des services e-commerce...$(NC)"
	docker-compose -f docker-compose.ecommerce.yml up -d
	@echo "$(GREEN)✅ Services e-commerce démarrés!$(NC)"
	@echo "🛒 APIs disponibles:"
	@echo "  • Customers API: http://localhost:8006"
	@echo "  • Cart API: http://localhost:8007" 
	@echo "  • Orders API: http://localhost:8008"
	@echo "  • Load Balancer: http://localhost:8080"

stop-ecommerce: ## 🛑 Arrêter tous les services e-commerce
	@echo "$(YELLOW)🛑 Arrêt des services e-commerce...$(NC)"
	docker-compose -f docker-compose.ecommerce.yml down

# ================================
# COMMANDES GLOBALES
# ================================

build: build-store build-ecommerce ## 🏗️ Construire TOUS les services

start: start-store start-ecommerce ## 🚀 Démarrer TOUS les services
	@echo ""
	@echo "$(GREEN)🎉 ÉCOSYSTÈME COMPLET DÉMARRÉ!$(NC)"
	@echo ""
	@echo "$(CYAN)🏪 Services Magasin:$(NC)"
	@echo "  • Products API: http://localhost:8001"
	@echo "  • Stores API: http://localhost:8002"
	@echo "  • Sales API: http://localhost:8003"
	@echo "  • Stock API: http://localhost:8004"
	@echo "  • Reporting API: http://localhost:8005"
	@echo ""
	@echo "$(YELLOW)🛒 Services E-Commerce:$(NC)"
	@echo "  • Customers API: http://localhost:8006"
	@echo "  • Cart API: http://localhost:8007"
	@echo "  • Orders API: http://localhost:8008"

stop: stop-store stop-ecommerce ## 🛑 Arrêter TOUS les services

restart: stop start ## 🔄 Redémarrer TOUS les services

# ================================
# LOGS ET MONITORING
# ================================

logs-store: ## 📜 Voir les logs des services magasin
	docker-compose -f docker-compose.yml logs -f

logs-ecommerce: ## 📜 Voir les logs des services e-commerce
	docker-compose -f docker-compose.ecommerce.yml logs -f

logs: ## 📜 Voir TOUS les logs
	@echo "$(CYAN)📜 Logs des services magasin:$(NC)"
	docker-compose -f docker-compose.yml logs --tail=50
	@echo ""
	@echo "$(YELLOW)📜 Logs des services e-commerce:$(NC)"
	docker-compose -f docker-compose.ecommerce.yml logs --tail=50

status: ## 📊 Vérifier le statut de tous les services
	@echo "$(CYAN)📊 Statut des services:$(NC)"
	@echo ""
	@echo "$(GREEN)🏪 Services Magasin:$(NC)"
	@docker-compose -f docker-compose.yml ps
	@echo ""
	@echo "$(YELLOW)🛒 Services E-Commerce:$(NC)"
	@docker-compose -f docker-compose.ecommerce.yml ps

# ================================
# TESTS
# ================================

test-store: ## 🧪 Exécuter les tests des services magasin
	@echo "$(CYAN)🧪 Tests des services magasin...$(NC)"
	cd services && python run_all_tests.py

test-ecommerce: ## 🧪 Exécuter les tests des services e-commerce
	@echo "$(CYAN)🧪 Tests des services e-commerce...$(NC)"
	@echo "🧑‍💼 Test Customers API..."
	cd services/customers-api && python -m pytest tests/ -v
	@echo "🛒 Test Cart API..."
	cd services/cart-api && python -m pytest tests/ -v
	@echo "📦 Test Orders API..."
	cd services/orders-api && python -m pytest tests/ -v

test: test-store test-ecommerce ## 🧪 Exécuter TOUS les tests

# ================================
# INITIALISATION ET NETTOYAGE
# ================================

init-data: ## 📊 Initialiser les données de test
	@echo "$(CYAN)📊 Initialisation des données de test...$(NC)"
	@echo "🏪 Initialisation services magasin..."
	cd services/products-api/src && python init_db.py
	cd services/stores-api/src && python init_db.py
	@echo "🛒 Initialisation services e-commerce..."
	cd services/customers-api/src && python init_db.py
	@echo "$(GREEN)✅ Données de test initialisées!$(NC)"

clean: ## 🧹 Nettoyer les containers et volumes
	@echo "$(RED)🧹 Nettoyage des containers et volumes...$(NC)"
	docker-compose -f docker-compose.yml down -v
	docker-compose -f docker-compose.ecommerce.yml down -v
	docker system prune -f
	@echo "$(GREEN)✅ Nettoyage terminé!$(NC)"

# ================================
# DÉVELOPPEMENT
# ================================

dev-customers: ## 🔧 Mode développement Customers API
	cd services/customers-api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8006

dev-cart: ## 🔧 Mode développement Cart API
	cd services/cart-api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8007

dev-orders: ## 🔧 Mode développement Orders API
	cd services/orders-api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8008

# ================================
# DOCUMENTATION
# ================================

docs: ## 📚 Ouvrir la documentation des APIs
	@echo "$(CYAN)📚 Documentation des APIs:$(NC)"
	@echo "🏪 Services Magasin:"
	@echo "  • Products API: http://localhost:8001/docs"
	@echo "  • Stores API: http://localhost:8002/docs"
	@echo "  • Sales API: http://localhost:8003/docs"
	@echo "  • Stock API: http://localhost:8004/docs"
	@echo "  • Reporting API: http://localhost:8005/docs"
	@echo ""
	@echo "🛒 Services E-Commerce:"
	@echo "  • Customers API: http://localhost:8006/docs"
	@echo "  • Cart API: http://localhost:8007/docs"
	@echo "  • Orders API: http://localhost:8008/docs" 