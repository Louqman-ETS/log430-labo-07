import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from decimal import Decimal

from src.api.main import app
from src.api.v1.dependencies import api_token_auth
from src.api.v1.endpoints.products import get_product_service
from src.api.v1.domain.products.entities.product import Product
from src.api.v1.domain.products.schemas.product_schemas import (
    ProductResponse,
    ProductPage,
)


class TestProductsEndpoints:
    """Test suite for products endpoints with DDD architecture"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""

        def mock_auth():
            return "test-token"

        app.dependency_overrides[api_token_auth] = mock_auth

        with TestClient(app) as client:
            yield client

        # Clean up
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_product_service(self):
        """Mock product service"""
        service = MagicMock()
        app.dependency_overrides[get_product_service] = lambda: service
        yield service
        # Clean up
        if get_product_service in app.dependency_overrides:
            del app.dependency_overrides[get_product_service]

    def test_get_products_success(self, client, mock_product_service):
        """Test successful retrieval of products list"""
        # Arrange
        mock_page = ProductPage(
            total=2,
            page=1,
            size=20,
            items=[
                ProductResponse(
                    id=1,
                    code="PROD001",
                    nom="Produit Test 1",
                    description="Description du produit 1",
                    prix=Decimal("19.99"),
                    quantite_stock=100,
                    categorie_id=1,
                ),
                ProductResponse(
                    id=2,
                    code="PROD002",
                    nom="Produit Test 2",
                    description="Description du produit 2",
                    prix=Decimal("29.99"),
                    quantite_stock=50,
                    categorie_id=2,
                ),
            ],
        )
        mock_product_service.get_products_paginated.return_value = mock_page

        # Act
        response = client.get("/api/v1/products")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 20
        assert len(data["items"]) == 2
        assert data["items"][0]["code"] == "PROD001"
        mock_product_service.get_products_paginated.assert_called_once_with(
            page=1, size=20
        )

    def test_get_products_with_pagination(self, client, mock_product_service):
        """Test products retrieval with pagination parameters"""
        # Arrange
        mock_page = ProductPage(total=100, page=3, size=10, items=[])
        mock_product_service.get_products_paginated.return_value = mock_page

        # Act
        response = client.get("/api/v1/products?page=3&size=10")

        # Assert
        assert response.status_code == 200
        mock_product_service.get_products_paginated.assert_called_once_with(
            page=3, size=10
        )

    def test_get_product_by_id_success(self, client, mock_product_service):
        """Test successful retrieval of product by ID"""
        # Arrange
        mock_response = ProductResponse(
            id=1,
            code="PROD001",
            nom="Produit Test",
            description="Description du produit",
            prix=Decimal("19.99"),
            quantite_stock=100,
            categorie_id=1,
        )
        mock_product_service.get_product_by_id.return_value = mock_response

        # Act
        response = client.get("/api/v1/products/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["code"] == "PROD001"
        assert data["nom"] == "Produit Test"
        mock_product_service.get_product_by_id.assert_called_once_with(1)

    def test_get_product_by_id_not_found(self, client, mock_product_service):
        """Test product not found by ID"""
        # Arrange
        mock_product_service.get_product_by_id.return_value = None

        # Act
        response = client.get("/api/v1/products/999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"
        assert "Product with identifier 999 not found" in data["message"]

    def test_create_product_success(self, client, mock_product_service):
        """Test successful product creation"""
        # Arrange
        product_data = {
            "code": "NEWPROD",
            "nom": "Nouveau Produit",
            "description": "Description du nouveau produit",
            "prix": 25.99,
            "quantite_stock": 75,
            "categorie_id": 1,
        }
        mock_response = ProductResponse(
            id=3,
            code="NEWPROD",
            nom="Nouveau Produit",
            description="Description du nouveau produit",
            prix=Decimal("25.99"),
            quantite_stock=75,
            categorie_id=1,
        )
        mock_product_service.create_product.return_value = mock_response

        # Act
        response = client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 3
        assert data["code"] == "NEWPROD"
        assert data["nom"] == "Nouveau Produit"
        mock_product_service.create_product.assert_called_once()

    def test_create_product_duplicate_code(self, client, mock_product_service):
        """Test product creation with duplicate code"""
        # Arrange
        product_data = {
            "code": "EXISTING",
            "nom": "Produit Existant",
            "prix": 19.99,
            "quantite_stock": 10,
            "categorie_id": 1,
        }
        mock_product_service.create_product.side_effect = ValueError(
            "Product with code 'EXISTING' already exists"
        )

        # Act
        response = client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_RESOURCE"

    def test_create_product_validation_error(self, client, mock_product_service):
        """Test product creation with validation error"""
        # Arrange
        product_data = {
            "code": "",  # Code vide
            "nom": "Produit",
            "prix": -10,  # Prix négatif
        }

        # Act
        response = client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_update_product_success(self, client, mock_product_service):
        """Test successful product update"""
        # Arrange
        update_data = {"nom": "Produit Modifié", "prix": 35.99, "quantite_stock": 200}
        mock_response = ProductResponse(
            id=1,
            code="PROD001",
            nom="Produit Modifié",
            description="Description",
            prix=Decimal("35.99"),
            quantite_stock=200,
            categorie_id=1,
        )
        mock_product_service.update_product.return_value = mock_response

        # Act
        response = client.put("/api/v1/products/1", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Produit Modifié"
        assert float(data["prix"]) == 35.99
        assert data["quantite_stock"] == 200

    def test_update_product_not_found(self, client, mock_product_service):
        """Test update of non-existent product"""
        # Arrange
        update_data = {"nom": "Produit Inexistant"}
        mock_product_service.update_product.return_value = None

        # Act
        response = client.put("/api/v1/products/999", json=update_data)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_patch_product_success(self, client, mock_product_service):
        """Test successful partial product update"""
        # Arrange
        patch_data = {"quantite_stock": 150}
        mock_response = ProductResponse(
            id=1,
            code="PROD001",
            nom="Produit Test",
            description="Description",
            prix=Decimal("19.99"),
            quantite_stock=150,
            categorie_id=1,
        )
        mock_product_service.update_product.return_value = mock_response

        # Act
        response = client.patch("/api/v1/products/1", json=patch_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quantite_stock"] == 150

    def test_delete_product_success(self, client, mock_product_service):
        """Test successful product deletion"""
        # Arrange
        mock_response = ProductResponse(
            id=1,
            code="PROD001",
            nom="Produit à Supprimer",
            description="Description",
            prix=Decimal("19.99"),
            quantite_stock=100,
            categorie_id=1,
        )
        mock_product_service.get_product_by_id.return_value = mock_response
        mock_product_service.delete_product.return_value = True

        # Act
        response = client.delete("/api/v1/products/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["code"] == "PROD001"

    def test_delete_product_not_found(self, client, mock_product_service):
        """Test deletion of non-existent product"""
        # Arrange
        mock_product_service.get_product_by_id.return_value = None

        # Act
        response = client.delete("/api/v1/products/999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_get_product_by_code_success(self, client, mock_product_service):
        """Test successful retrieval of product by code"""
        # Arrange
        mock_response = ProductResponse(
            id=1,
            code="TESTCODE",
            nom="Produit Test",
            description="Description",
            prix=Decimal("19.99"),
            quantite_stock=100,
            categorie_id=1,
        )
        mock_product_service.get_product_by_code.return_value = mock_response

        # Act
        response = client.get("/api/v1/products/by-code/TESTCODE")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TESTCODE"
        mock_product_service.get_product_by_code.assert_called_once_with("TESTCODE")

    def test_get_product_by_code_not_found(self, client, mock_product_service):
        """Test product not found by code"""
        # Arrange
        mock_product_service.get_product_by_code.return_value = None

        # Act
        response = client.get("/api/v1/products/by-code/NOTFOUND")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_reduce_product_stock_success(self, client, mock_product_service):
        """Test successful stock reduction"""
        # Arrange
        mock_response = ProductResponse(
            id=1,
            code="PROD001",
            nom="Produit Test",
            description="Description",
            prix=Decimal("19.99"),
            quantite_stock=80,  # Reduced from 100
            categorie_id=1,
        )
        mock_product_service.reduce_product_stock.return_value = mock_response

        # Act
        response = client.post("/api/v1/products/1/reduce-stock?quantity=20")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quantite_stock"] == 80
        mock_product_service.reduce_product_stock.assert_called_once_with(1, 20)

    def test_reduce_product_stock_insufficient(self, client, mock_product_service):
        """Test stock reduction with insufficient stock"""
        # Arrange
        mock_product_service.reduce_product_stock.side_effect = ValueError(
            "Insufficient stock"
        )

        # Act
        response = client.post("/api/v1/products/1/reduce-stock?quantity=200")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "BUSINESS_LOGIC_ERROR"

    def test_get_low_stock_products_success(self, client, mock_product_service):
        """Test successful retrieval of low stock products"""
        # Arrange
        mock_products = [
            ProductResponse(
                id=1,
                code="LOW001",
                nom="Produit Stock Bas 1",
                description="Description",
                prix=Decimal("19.99"),
                quantite_stock=5,
                categorie_id=1,
            ),
            ProductResponse(
                id=2,
                code="LOW002",
                nom="Produit Stock Bas 2",
                description="Description",
                prix=Decimal("29.99"),
                quantite_stock=8,
                categorie_id=2,
            ),
        ]
        mock_product_service.get_low_stock_products.return_value = mock_products

        # Act
        response = client.get("/api/v1/products/low-stock/?threshold=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["quantite_stock"] == 5
        assert data[1]["quantite_stock"] == 8
        mock_product_service.get_low_stock_products.assert_called_once_with(10)

    def test_unauthorized_access(self, mock_product_service):
        """Test unauthorized access without token"""
        # Arrange
        client = TestClient(app)  # Client without mocked auth

        # Act
        response = client.get("/api/v1/products")

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "HTTP_ERROR"
