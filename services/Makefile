.PHONY: help build up down logs clean test status install-test-deps test test-products test-sales test-stock test-verbose test-quick coverage check-services integration-test benchmark

# Default target
help:
	@echo "🧪 Tests Unitaires - Microservices DDD"
	@echo "======================================"
	@echo ""
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Variables
PYTHON := python3
PIP := pip3

# Build all Docker images
build:
	@echo "Building all microservices..."
	docker-compose build

# Start all services
up:
	@echo "Starting all microservices..."
	docker-compose up -d
	@echo "Services starting..."
	@echo "Products API: http://localhost:8001/docs"
	@echo "Stores API: http://localhost:8002/docs"
	@echo "Sales API: http://localhost:8003/docs"
	@echo "Stock API: http://localhost:8004/docs"
	@echo "Reporting API: http://localhost:8005/docs"

# Stop all services
down:
	@echo "Stopping all microservices..."
	docker-compose down

# Restart all services
restart: down up

# Show logs
logs:
	docker-compose logs -f

# Show service status
status:
	@echo "=== Service Status ==="
	docker-compose ps
	@echo ""
	@echo "=== Health Checks ==="
	@echo "Products API:"
	@curl -s http://localhost:8001/health 2>/dev/null || echo "  Service not available"
	@echo ""
	@echo "Stores API:"
	@curl -s http://localhost:8002/health 2>/dev/null || echo "  Service not available"
	@echo ""
	@echo "Sales API:"
	@curl -s http://localhost:8003/health 2>/dev/null || echo "  Service not available"
	@echo ""
	@echo "Stock API:"
	@curl -s http://localhost:8004/health 2>/dev/null || echo "  Service not available"
	@echo ""
	@echo "Reporting API:"
	@curl -s http://localhost:8005/health 2>/dev/null || echo "  Service not available"
	@echo ""

# Clean everything (including volumes)
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "test*.db" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Nettoyage terminé!"

# Test all services
test:
	@echo "🧪 Exécution de tous les tests..."
	@$(PYTHON) run_all_tests.py

# Individual service commands
up-products:
	docker-compose up -d products-db products-api

up-stores:
	docker-compose up -d stores-db stores-api

up-reporting:
	docker-compose up -d reporting-db reporting-api

logs-products:
	docker-compose logs -f products-api

logs-stores:
	docker-compose logs -f stores-api

logs-reporting:
	docker-compose logs -f reporting-api

install-test-deps: ## Installe toutes les dépendances de test
	@echo "📦 Installation des dépendances de test..."
	@for service in products-api sales-api stock-api stores-api reporting-api; do \
		if [ -d "$$service" ]; then \
			echo "📦 Installing deps for $$service..."; \
			cd $$service && $(PIP) install -r requirements.txt && cd ..; \
		fi; \
	done
	@echo "✅ Toutes les dépendances installées!"

test-products: ## Teste uniquement le service Products
	@echo "🧪 Tests du service Products..."
	@cd products-api && $(PYTHON) -m pytest tests/ -v

test-sales: ## Teste uniquement le service Sales
	@echo "🧪 Tests du service Sales..."
	@cd sales-api && $(PYTHON) -m pytest tests/ -v

test-stock: ## Teste uniquement le service Stock
	@echo "🧪 Tests du service Stock..."
	@cd stock-api && $(PYTHON) -m pytest tests/ -v

test-stores: ## Teste uniquement le service Stores
	@echo "🧪 Tests du service Stores..."
	@cd stores-api && $(PYTHON) -m pytest tests/ -v

test-reporting: ## Teste uniquement le service Reporting  
	@echo "🧪 Tests du service Reporting..."
	@cd reporting-api && $(PYTHON) -m pytest tests/ -v

test-verbose: ## Exécute tous les tests avec sortie détaillée
	@echo "🧪 Tests détaillés de tous les services..."
	@for service in products-api sales-api stock-api; do \
		if [ -d "$$service/tests" ]; then \
			echo ""; \
			echo "📋 Testing $$service..."; \
			echo "----------------------------------------"; \
			cd $$service && $(PYTHON) -m pytest tests/ -v --tb=short && cd ..; \
		fi; \
	done

test-quick: ## Tests rapides (sans verbose)
	@echo "⚡ Tests rapides..."
	@for service in products-api sales-api stock-api; do \
		if [ -d "$$service/tests" ]; then \
			echo "Testing $$service..."; \
			cd $$service && $(PYTHON) -m pytest tests/ -q && cd ..; \
		fi; \
	done

coverage: ## Exécute les tests avec coverage
	@echo "📊 Tests avec couverture de code..."
	@for service in products-api sales-api stock-api; do \
		if [ -d "$$service/tests" ]; then \
			echo "Coverage for $$service..."; \
			cd $$service && $(PYTHON) -m pytest tests/ --cov=src --cov-report=term-missing && cd ..; \
		fi; \
	done

check-services: ## Vérifie que tous les services sont en cours d'exécution
	@echo "🔍 Vérification des services..."
	@for port in 8001 8002 8003 8004 8005; do \
		curl -s http://localhost:$$port/health >/dev/null && echo "✅ Service sur port $$port: OK" || echo "❌ Service sur port $$port: KO"; \
	done

integration-test: ## Tests d'intégration avec services en cours d'exécution
	@echo "🔗 Tests d'intégration..."
	@echo "Vérification que tous les services sont démarrés..."
	@make check-services
	@echo ""
	@echo "Tests des endpoints en conditions réelles..."
	@curl -s http://localhost:8001/api/v1/products/ | head -c 100 && echo "... ✅ Products API"
	@curl -s http://localhost:8003/api/v1/sales/ | head -c 100 && echo "... ✅ Sales API"
	@curl -s http://localhost:8004/api/v1/stock/alerts | head -c 100 && echo "... ✅ Stock API"

benchmark: ## Tests de performance basiques
	@echo "⚡ Tests de performance..."
	@echo "Test de charge sur l'endpoint products..."
	@for i in {1..10}; do \
		time curl -s http://localhost:8001/api/v1/products/ >/dev/null; \
	done 