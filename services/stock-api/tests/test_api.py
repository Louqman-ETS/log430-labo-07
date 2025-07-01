import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestStockAPI:
    """Tests pour les endpoints de base de l'API Stock"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "service" in data
        assert data["service"] == "stock"
        assert "features" in data
        assert "RESTful API" in data["features"]
        assert "Inventory Management" in data["features"]
    
    def test_health_check(self):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "stock"
        assert "timestamp" in data
    
    def test_request_id_header(self):
        """Test que le Request-ID est présent dans les headers"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8

class TestStockEndpoints:
    """Tests pour les endpoints de gestion des stocks"""
    
    def test_get_stock_alerts_empty(self):
        """Test récupération des alertes de stock"""
        response = client.get("/api/v1/stock/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total_alerts" in data
        assert "service" in data
        assert data["service"] == "stock"
        assert data["total_alerts"] == 0
        assert data["alerts"] == []
    
    def test_get_product_stock(self):
        """Test récupération du stock d'un produit"""
        product_id = 1
        response = client.get(f"/api/v1/products/{product_id}/stock")
        assert response.status_code == 200
        
        data = response.json()
        assert "product_id" in data
        assert "stock_quantity" in data
        assert "alert_threshold" in data
        assert "status" in data
        assert "service" in data
        assert data["product_id"] == product_id
        assert data["service"] == "stock"
    
    def test_reduce_product_stock(self):
        """Test réduction du stock d'un produit"""
        product_id = 1
        quantity = 5
        
        response = client.put(f"/api/v1/products/{product_id}/stock/reduce?quantity={quantity}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["product_id"] == product_id
        assert data["reduced_quantity"] == quantity
        assert "message" in data
        assert data["service"] == "stock"
    
    def test_increase_product_stock(self):
        """Test augmentation du stock d'un produit"""
        product_id = 1
        quantity = 10
        
        response = client.put(f"/api/v1/products/{product_id}/stock/increase?quantity={quantity}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["product_id"] == product_id
        assert data["increased_quantity"] == quantity
        assert "message" in data
        assert data["service"] == "stock"

class TestErrorHandling:
    """Tests pour la gestion d'erreurs standardisée"""
    
    def test_404_error_format(self):
        """Test du format d'erreur 404 standardisé"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Vérifier le header Request-ID
        assert "x-request-id" in response.headers
    
    def test_invalid_product_id(self):
        """Test avec un ID de produit invalide"""
        # Test avec un ID négatif
        response = client.get("/api/v1/products/-1/stock")
        assert response.status_code == 422  # Validation error
        
        # Test avec un ID non numérique sera capturé par FastAPI
        response = client.get("/api/v1/products/abc/stock")
        assert response.status_code == 422

class TestMiddleware:
    """Tests pour le middleware de logging"""
    
    def test_request_timing(self):
        """Test que les requêtes sont tracées avec timing"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Le middleware devrait ajouter un Request-ID
        assert "x-request-id" in response.headers
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8
        assert request_id.isalnum()
    
    def test_different_request_ids(self):
        """Test que chaque requête a un Request-ID différent"""
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        id1 = response1.headers["x-request-id"]
        id2 = response2.headers["x-request-id"]
        
        assert id1 != id2

class TestBusinessLogic:
    """Tests pour la logique métier du stock"""
    
    def test_stock_reduction_workflow(self):
        """Test du workflow de réduction de stock"""
        product_id = 1
        
        # Obtenir le stock initial
        response = client.get(f"/api/v1/products/{product_id}/stock")
        assert response.status_code == 200
        initial_data = response.json()
        initial_stock = initial_data["stock_quantity"]
        
        # Réduire le stock
        quantity_to_reduce = 3
        response = client.put(f"/api/v1/products/{product_id}/stock/reduce?quantity={quantity_to_reduce}")
        assert response.status_code == 200
        
        reduction_data = response.json()
        assert reduction_data["success"] is True
        assert reduction_data["reduced_quantity"] == quantity_to_reduce
    
    def test_stock_increase_workflow(self):
        """Test du workflow d'augmentation de stock"""
        product_id = 2
        
        # Augmenter le stock
        quantity_to_add = 15
        response = client.put(f"/api/v1/products/{product_id}/stock/increase?quantity={quantity_to_add}")
        assert response.status_code == 200
        
        increase_data = response.json()
        assert increase_data["success"] is True
        assert increase_data["increased_quantity"] == quantity_to_add
    
    def test_zero_quantity_operations(self):
        """Test des opérations avec quantité zéro"""
        product_id = 1
        
        # Réduction avec quantité zéro
        response = client.put(f"/api/v1/products/{product_id}/stock/reduce?quantity=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reduced_quantity"] == 0 