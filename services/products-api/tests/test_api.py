import pytest
import json
from fastapi.testclient import TestClient

class TestProductsAPI:
    """Tests pour les endpoints de l'API Products"""
    
    def test_root_endpoint(self, client):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "service" in data
        assert data["service"] == "products"
        assert "features" in data
        assert "RESTful API" in data["features"]
        assert "Structured Logging" in data["features"]
    
    def test_health_check(self, client):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "products"
        assert "timestamp" in data
    
    def test_request_id_header(self, client):
        """Test que le Request-ID est présent dans les headers"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        
        # Le Request-ID doit être une chaîne de 8 caractères
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8

class TestCategoriesEndpoints:
    """Tests pour les endpoints des catégories"""
    
    def test_get_categories_empty(self, client):
        """Test récupération des catégories quand la base est vide"""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_categories_with_data(self, client, sample_category):
        """Test récupération des catégories avec données"""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["nom"] == "Test Category"
    
    def test_create_category(self, client):
        """Test création d'une catégorie"""
        category_data = {
            "nom": "Nouvelle Catégorie",
            "description": "Description de test"
        }
        
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["nom"] == category_data["nom"]
        assert data["description"] == category_data["description"]
        assert "id" in data
    
    def test_get_category_by_id(self, client, sample_category):
        """Test récupération d'une catégorie par ID"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_category.id
        assert data["nom"] == sample_category.nom
    
    def test_get_category_not_found(self, client):
        """Test récupération d'une catégorie inexistante - doit tester notre gestion d'erreurs"""
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404
        
        data = response.json()
        # Test du format d'erreur standardisé
        assert "error" in data
        assert data["error"]["code"] == 404
        assert "not found" in data["error"]["message"].lower()
        assert data["error"]["type"] == "http_error"
        assert data["error"]["service"] == "products"
        assert "request_id" in data["error"]

class TestProductsEndpoints:
    """Tests pour les endpoints des produits"""
    
    def test_get_products_empty(self, client):
        """Test récupération des produits quand la base est vide"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 20
    
    def test_get_products_with_data(self, client, sample_product):
        """Test récupération des produits avec données"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        
        product = data["items"][0]
        assert product["nom"] == "Test Product"
        assert product["prix"] == 9.99
        assert "category" in product
    
    def test_get_products_pagination(self, client, multiple_products):
        """Test de la pagination des produits"""
        # Test première page
        response = client.get("/api/v1/products/?page=1&size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 2
        
        # Test deuxième page
        response = client.get("/api/v1/products/?page=2&size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 5  # Derniers 5 produits
    
    def test_create_product(self, client, sample_category):
        """Test création d'un produit"""
        product_data = {
            "code": "NEWPROD001",
            "nom": "Nouveau Produit",
            "description": "Un super produit",
            "prix": 15.99,
            "categorie_id": sample_category.id
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["nom"] == product_data["nom"]
        assert data["prix"] == product_data["prix"]
        assert data["categorie_id"] == sample_category.id
        assert "id" in data
    
    def test_create_product_invalid_category(self, client):
        """Test création d'un produit avec catégorie inexistante"""
        product_data = {
            "code": "INVALID001",
            "nom": "Produit Invalide",
            "description": "Catégorie inexistante",
            "prix": 10.0,
            "categorie_id": 99999
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 400
    
    def test_get_product_by_id(self, client, sample_product):
        """Test récupération d'un produit par ID"""
        response = client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_product.id
        assert data["nom"] == sample_product.nom
        assert "category" in data
    
    def test_get_product_not_found(self, client):
        """Test récupération d'un produit inexistant"""
        response = client.get("/api/v1/products/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == 404
        assert "99999" in data["error"]["message"]
        assert data["error"]["service"] == "products"
    
    def test_update_product(self, client, sample_product):
        """Test mise à jour d'un produit"""
        update_data = {
            "nom": "Produit Modifié",
            "prix": 19.99
        }
        
        response = client.put(f"/api/v1/products/{sample_product.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nom"] == update_data["nom"]
        assert data["prix"] == update_data["prix"]
    
    def test_delete_product(self, client, sample_product):
        """Test suppression d'un produit"""
        response = client.delete(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        
        # Vérifier que le produit n'existe plus
        response = client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 404

class TestErrorHandling:
    """Tests spécifiques pour la gestion d'erreurs standardisée"""
    
    def test_404_error_format(self, client):
        """Test du format d'erreur 404 standardisé"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Vérifier le header Request-ID
        assert "x-request-id" in response.headers
    
    def test_validation_error_format(self, client):
        """Test du format d'erreur de validation"""
        invalid_data = {
            "nom": "",  # Nom vide
            "prix": -5.0,  # Prix négatif
        }
        
        response = client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # FastAPI renvoie automatiquement les erreurs de validation
        assert "x-request-id" in response.headers

class TestMiddleware:
    """Tests pour le middleware de logging"""
    
    def test_request_timing(self, client):
        """Test que les requêtes sont tracées avec timing"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Le middleware devrait ajouter un Request-ID
        assert "x-request-id" in response.headers
        request_id = response.headers["x-request-id"]
        assert len(request_id) == 8
        assert request_id.isalnum()

class TestBusinessLogic:
    """Tests pour la logique métier spécifique"""
    
    def test_product_category_relationship(self, client, sample_product):
        """Test de la relation entre produit et catégorie"""
        response = client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "category" in data
        assert data["category"]["nom"] == "Test Category"
        assert data["categorie_id"] == sample_product.categorie_id
    
    def test_product_crud_workflow(self, client, sample_category):
        """Test du workflow complet CRUD des produits"""
        # Créer un produit
        product_data = {
            "code": "WORKFLOW001",
            "nom": "Produit Workflow",
            "description": "Test complet",
            "prix": 29.99,
            "categorie_id": sample_category.id
        }
        
        # CREATE
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # READ
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["nom"] == product_data["nom"]
        
        # UPDATE
        update_data = {"nom": "Produit Modifié", "prix": 39.99}
        response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["nom"] == "Produit Modifié"
        
        # DELETE
        response = client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        
        # Vérifier que le produit n'existe plus
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 404 