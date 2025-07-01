import pytest
import json
from fastapi.testclient import TestClient

class TestSalesAPI:
    """Tests pour les endpoints de base de l'API Sales"""
    
    def test_root_endpoint(self, client):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "service" in data
        assert data["service"] == "sales"
        assert "features" in data
        assert "RESTful API" in data["features"]
        assert "Inter-service Communication" in data["features"]
    
    def test_health_check(self, client):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sales"
        assert "timestamp" in data
    
    def test_request_id_header(self, client):
        """Test que le Request-ID est présent dans les headers"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8

class TestSalesEndpoints:
    """Tests pour les endpoints des ventes"""
    
    def test_get_sales_empty(self, client):
        """Test récupération des ventes quand la base est vide"""
        response = client.get("/api/v1/sales/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_sales_with_data(self, client, sample_sale):
        """Test récupération des ventes avec données"""
        response = client.get("/api/v1/sales/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_sale.id
        assert data[0]["total"] == sample_sale.total
        assert "sale_lines" in data[0]
        assert len(data[0]["sale_lines"]) == 2
    
    def test_get_sale_by_id(self, client, sample_sale):
        """Test récupération d'une vente par ID"""
        response = client.get(f"/api/v1/sales/{sample_sale.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_sale.id
        assert data["store_id"] == sample_sale.store_id
        assert data["total"] == sample_sale.total
        assert "sale_lines" in data
    
    def test_get_sale_not_found(self, client):
        """Test récupération d'une vente inexistante"""
        response = client.get("/api/v1/sales/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 404
        assert data["error"]["service"] == "sales"
        assert "request_id" in data["error"]

class TestSaleCreation:
    """Tests pour la création de ventes avec inter-service communication"""
    
    def test_create_sale_success(self, client, mock_external_services, valid_sale_data):
        """Test création d'une vente avec succès"""
        response = client.post("/api/v1/sales/", json=valid_sale_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["store_id"] == valid_sale_data["store_id"]
        assert data["cash_register_id"] == valid_sale_data["cash_register_id"]
        assert data["notes"] == valid_sale_data["notes"]
        assert data["total"] == 27.48  # 2 * 10.99 + 1 * 5.50
        assert "sale_lines" in data
        assert len(data["sale_lines"]) == 2
    
    def test_create_sale_invalid_store(self, client, mock_external_services):
        """Test création d'une vente avec magasin inexistant"""
        invalid_data = {
            "store_id": 999,  # Store inexistant
            "cash_register_id": 1,
            "sale_lines": [
                {"product_id": 1, "quantite": 1, "prix_unitaire": 10.99}
            ]
        }
        
        response = client.post("/api/v1/sales/", json=invalid_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 400
        assert "validation failed" in data["error"]["message"].lower()
    
    def test_create_sale_invalid_product(self, client, mock_external_services):
        """Test création d'une vente avec produit inexistant"""
        invalid_data = {
            "store_id": 1,
            "cash_register_id": 1,
            "sale_lines": [
                {"product_id": 999, "quantite": 1, "prix_unitaire": 10.99}  # Produit inexistant
            ]
        }
        
        response = client.post("/api/v1/sales/", json=invalid_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 400
        assert "validation failed" in data["error"]["message"].lower()
    
    def test_create_sale_empty_lines(self, client, mock_external_services):
        """Test création d'une vente sans lignes de vente"""
        invalid_data = {
            "store_id": 1,
            "cash_register_id": 1,
            "sale_lines": []  # Pas de lignes de vente
        }
        
        response = client.post("/api/v1/sales/", json=invalid_data)
        assert response.status_code == 422  # Validation Pydantic
    
    def test_create_sale_negative_quantity(self, client, mock_external_services):
        """Test création d'une vente avec quantité négative"""
        invalid_data = {
            "store_id": 1,
            "cash_register_id": 1,
            "sale_lines": [
                {"product_id": 1, "quantite": -1, "prix_unitaire": 10.99}  # Quantité négative
            ]
        }
        
        response = client.post("/api/v1/sales/", json=invalid_data)
        assert response.status_code == 422  # Validation Pydantic

class TestSalesStats:
    """Tests pour les statistiques des ventes"""
    
    def test_get_stats_empty(self, client):
        """Test des statistiques quand aucune vente"""
        response = client.get("/api/v1/sales/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_sales"] == 0
        assert data["total_revenue"] == 0.0
        assert data["average_sale_amount"] == 0.0
    
    def test_get_stats_with_data(self, client, sample_sale):
        """Test des statistiques avec données"""
        response = client.get("/api/v1/sales/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_sales"] == 1
        assert data["total_revenue"] == sample_sale.total
        assert data["average_sale_amount"] == sample_sale.total

class TestSalesByStore:
    """Tests pour les ventes par magasin"""
    
    def test_get_sales_by_store(self, client, sample_sale):
        """Test récupération des ventes par magasin"""
        response = client.get(f"/api/v1/sales/store/{sample_sale.store_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["store_id"] == sample_sale.store_id
    
    def test_get_sales_by_nonexistent_store(self, client):
        """Test récupération des ventes d'un magasin inexistant"""
        response = client.get("/api/v1/sales/store/999")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0  # Aucune vente pour ce magasin

class TestInterServiceCommunication:
    """Tests spécifiques pour l'inter-service communication"""
    
    def test_stock_reduction_called(self, client, mock_external_services, valid_sale_data):
        """Test que l'API Stock est appelée pour réduire le stock"""
        response = client.post("/api/v1/sales/", json=valid_sale_data)
        assert response.status_code == 200
        
        # Vérifier que les bonnes URLs ont été appelées
        calls = mock_external_services.calls
        
        # Vérification des produits
        product_calls = [call for call in calls if "products-api" in str(call.request.url)]
        assert len(product_calls) == 2  # 2 produits validés
        
        # Vérification du store
        store_calls = [call for call in calls if "stores-api" in str(call.request.url) and "stores" in str(call.request.url)]
        assert len(store_calls) == 1
        
        # Vérification de la réduction de stock
        stock_calls = [call for call in calls if "stock-api" in str(call.request.url)]
        assert len(stock_calls) == 2  # 2 réductions de stock
    
    def test_validation_workflow(self, client, mock_external_services, valid_sale_data):
        """Test du workflow complet de validation inter-service"""
        response = client.post("/api/v1/sales/", json=valid_sale_data)
        assert response.status_code == 200
        
        # Vérifier l'ordre des appels
        calls = mock_external_services.calls
        
        # Premier appel : validation du store
        assert "stores/1" in str(calls[0].request.url)
        
        # Deuxième appel : validation de la caisse
        assert "cash-registers/1" in str(calls[1].request.url)
        
        # Appels suivants : validation des produits
        product_calls = [call for call in calls[2:4]]
        assert all("products" in str(call.request.url) for call in product_calls)

class TestErrorHandling:
    """Tests pour la gestion d'erreurs standardisée"""
    
    def test_error_format_consistency(self, client):
        """Test de la cohérence du format d'erreur"""
        response = client.get("/api/v1/sales/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "type" in data["error"]
        assert "request_id" in data["error"]
        assert "service" in data["error"]
        assert data["error"]["service"] == "sales"
    
    def test_request_id_in_headers(self, client):
        """Test que le Request-ID est dans les headers même en cas d'erreur"""
        response = client.get("/api/v1/sales/99999")
        assert response.status_code == 404
        assert "x-request-id" in response.headers

class TestLoggingMiddleware:
    """Tests pour le middleware de logging"""
    
    def test_middleware_adds_request_id(self, client):
        """Test que le middleware ajoute un Request-ID"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8
        assert request_id.isalnum()
    
    def test_different_request_ids(self, client):
        """Test que chaque requête a un Request-ID différent"""
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        id1 = response1.headers["x-request-id"]
        id2 = response2.headers["x-request-id"]
        
        assert id1 != id2

class TestBusinessLogic:
    """Tests pour la logique métier complexe"""
    
    def test_total_calculation(self, client, mock_external_services, valid_sale_data):
        """Test du calcul correct du total"""
        response = client.post("/api/v1/sales/", json=valid_sale_data)
        assert response.status_code == 200
        
        data = response.json()
        expected_total = (2 * 10.99) + (1 * 5.50)  # 27.48
        assert data["total"] == expected_total
        
        # Vérifier les sous-totaux des lignes
        lines = data["sale_lines"]
        assert lines[0]["sous_total"] == 2 * 10.99  # 21.98
        assert lines[1]["sous_total"] == 1 * 5.50   # 5.50
    
    def test_sale_lines_creation(self, client, mock_external_services, valid_sale_data):
        """Test de la création correcte des lignes de vente"""
        response = client.post("/api/v1/sales/", json=valid_sale_data)
        assert response.status_code == 200
        
        data = response.json()
        lines = data["sale_lines"]
        
        assert len(lines) == 2
        
        # Première ligne
        assert lines[0]["product_id"] == 1
        assert lines[0]["quantite"] == 2
        assert lines[0]["prix_unitaire"] == 10.99
        
        # Deuxième ligne
        assert lines[1]["product_id"] == 2
        assert lines[1]["quantite"] == 1
        assert lines[1]["prix_unitaire"] == 5.50 