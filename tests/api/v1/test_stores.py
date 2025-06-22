import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from src.api.main import app
from src.api.v1.dependencies import api_token_auth
from src.api.v1.endpoints.stores import get_store_service
from src.api.v1.domain.stores.entities.store import Store
from src.api.v1.domain.stores.schemas.store_schemas import StoreResponse, StorePage
from src.api.v1.errors import NotFoundError, DuplicateError, BusinessLogicError


# Mock data
MOCK_STORE_1 = Store(
    id=1,
    nom="Magasin Centre-Ville",
    adresse="123 Rue Saint-Catherine, Montréal",
    telephone="514-123-4567",
    email="centre@magasin.com",
)

MOCK_STORE_2 = Store(
    id=2,
    nom="Magasin Express",
    adresse="456 Boulevard Saint-Laurent",
    telephone="514-987-6543",
    email="express@magasin.com",
)

MOCK_STORES = [MOCK_STORE_1, MOCK_STORE_2]


class TestStoresEndpoints:
    """Test suite for stores endpoints with DDD architecture"""

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
    def mock_store_service(self):
        """Mock store service"""
        service = MagicMock()
        app.dependency_overrides[get_store_service] = lambda: service
        yield service
        # Clean up
        if get_store_service in app.dependency_overrides:
            del app.dependency_overrides[get_store_service]

    def test_get_stores_success(self, client, mock_store_service):
        """Test successful retrieval of stores list"""
        # Arrange
        mock_page = StorePage(
            total=2,
            page=1,
            size=20,
            items=[
                StoreResponse(
                    id=1,
                    nom="Magasin Centre-Ville",
                    adresse="123 Rue Saint-Catherine, Montréal",
                    telephone="514-123-4567",
                    email="centre@magasin.com",
                ),
                StoreResponse(
                    id=2,
                    nom="Magasin Express",
                    adresse="456 Boulevard Saint-Laurent",
                    telephone="514-987-6543",
                    email="express@magasin.com",
                ),
            ],
        )
        mock_store_service.get_stores_paginated.return_value = mock_page

        # Act
        response = client.get("/api/v1/stores")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 20
        assert len(data["items"]) == 2
        assert data["items"][0]["nom"] == "Magasin Centre-Ville"
        mock_store_service.get_stores_paginated.assert_called_once_with(page=1, size=20)

    def test_get_stores_with_pagination(self, client, mock_store_service):
        """Test stores retrieval with pagination parameters"""
        # Arrange
        mock_page = StorePage(total=10, page=2, size=5, items=[])
        mock_store_service.get_stores_paginated.return_value = mock_page

        # Act
        response = client.get("/api/v1/stores?page=2&size=5")

        # Assert
        assert response.status_code == 200
        mock_store_service.get_stores_paginated.assert_called_once_with(page=2, size=5)

    def test_get_store_by_id_success(self, client, mock_store_service):
        """Test successful retrieval of store by ID"""
        # Arrange
        mock_response = StoreResponse(
            id=1,
            nom="Magasin Centre-Ville",
            adresse="123 Rue Saint-Catherine, Montréal",
            telephone="514-123-4567",
            email="centre@magasin.com",
        )
        mock_store_service.get_store_by_id.return_value = mock_response

        # Act
        response = client.get("/api/v1/stores/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["nom"] == "Magasin Centre-Ville"
        mock_store_service.get_store_by_id.assert_called_once_with(1)

    def test_get_store_by_id_not_found(self, client, mock_store_service):
        """Test store not found by ID"""
        # Arrange
        mock_store_service.get_store_by_id.return_value = None

        # Act
        response = client.get("/api/v1/stores/999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"
        assert "Store with identifier 999 not found" in data["message"]

    def test_create_store_success(self, client, mock_store_service):
        """Test successful store creation"""
        # Arrange
        store_data = {
            "nom": "Nouveau Magasin",
            "adresse": "789 Rue Sherbrooke",
            "telephone": "514-555-0123",
            "email": "nouveau@magasin.com",
        }
        mock_response = StoreResponse(
            id=3,
            nom="Nouveau Magasin",
            adresse="789 Rue Sherbrooke",
            telephone="514-555-0123",
            email="nouveau@magasin.com",
        )
        mock_store_service.create_store.return_value = mock_response

        # Act
        response = client.post("/api/v1/stores/", json=store_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 3
        assert data["nom"] == "Nouveau Magasin"
        mock_store_service.create_store.assert_called_once()

    def test_create_store_duplicate_name(self, client, mock_store_service):
        """Test store creation with duplicate name"""
        # Arrange
        store_data = {"nom": "Magasin Existant", "adresse": "789 Rue Sherbrooke"}
        mock_store_service.create_store.side_effect = ValueError(
            "Store with name 'Magasin Existant' already exists"
        )

        # Act
        response = client.post("/api/v1/stores/", json=store_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "DUPLICATE_RESOURCE"

    def test_create_store_validation_error(self, client, mock_store_service):
        """Test store creation with validation error"""
        # Arrange
        store_data = {"nom": "", "adresse": "789 Rue Sherbrooke"}  # Nom vide

        # Act
        response = client.post("/api/v1/stores/", json=store_data)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_update_store_success(self, client, mock_store_service):
        """Test successful store update"""
        # Arrange
        update_data = {"nom": "Magasin Modifié", "telephone": "514-555-9999"}
        mock_response = StoreResponse(
            id=1,
            nom="Magasin Modifié",
            adresse="123 Rue Saint-Catherine, Montréal",
            telephone="514-555-9999",
            email="centre@magasin.com",
        )
        mock_store_service.update_store.return_value = mock_response

        # Act
        response = client.put("/api/v1/stores/1", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Magasin Modifié"
        assert data["telephone"] == "514-555-9999"

    def test_update_store_not_found(self, client, mock_store_service):
        """Test update of non-existent store"""
        # Arrange
        update_data = {"nom": "Magasin Inexistant"}
        mock_store_service.update_store.return_value = None

        # Act
        response = client.put("/api/v1/stores/999", json=update_data)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_patch_store_success(self, client, mock_store_service):
        """Test successful partial store update"""
        # Arrange
        patch_data = {"telephone": "514-555-8888"}
        mock_response = StoreResponse(
            id=1,
            nom="Magasin Centre-Ville",
            adresse="123 Rue Saint-Catherine, Montréal",
            telephone="514-555-8888",
            email="centre@magasin.com",
        )
        mock_store_service.update_store.return_value = mock_response

        # Act
        response = client.patch("/api/v1/stores/1", json=patch_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["telephone"] == "514-555-8888"

    def test_delete_store_success(self, client, mock_store_service):
        """Test successful store deletion"""
        # Arrange
        mock_response = StoreResponse(
            id=1,
            nom="Magasin à Supprimer",
            adresse="123 Rue Test",
            telephone="514-555-0000",
            email="test@magasin.com",
        )
        mock_store_service.get_store_by_id.return_value = mock_response
        mock_store_service.delete_store.return_value = True

        # Act
        response = client.delete("/api/v1/stores/1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["nom"] == "Magasin à Supprimer"

    def test_delete_store_not_found(self, client, mock_store_service):
        """Test deletion of non-existent store"""
        # Arrange
        mock_store_service.get_store_by_id.return_value = None

        # Act
        response = client.delete("/api/v1/stores/999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_get_store_by_name_success(self, client, mock_store_service):
        """Test successful retrieval of store by name"""
        # Arrange
        mock_response = StoreResponse(
            id=1,
            nom="Magasin Centre-Ville",
            adresse="123 Rue Saint-Catherine, Montréal",
            telephone="514-123-4567",
            email="centre@magasin.com",
        )
        mock_store_service.get_store_by_name.return_value = mock_response

        # Act
        response = client.get("/api/v1/stores/by-name/Magasin Centre-Ville")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Magasin Centre-Ville"

    def test_get_store_by_name_not_found(self, client, mock_store_service):
        """Test store not found by name"""
        # Arrange
        mock_store_service.get_store_by_name.return_value = None

        # Act
        response = client.get("/api/v1/stores/by-name/Inexistant")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_update_store_contact_success(self, client, mock_store_service):
        """Test successful store contact update"""
        # Arrange
        mock_response = StoreResponse(
            id=1,
            nom="Magasin Centre-Ville",
            adresse="123 Rue Saint-Catherine, Montréal",
            telephone="514-999-9999",
            email="nouveau@magasin.com",
        )
        mock_store_service.update_store_contact.return_value = mock_response

        # Act
        response = client.post(
            "/api/v1/stores/1/update-contact?email=nouveau@magasin.com&telephone=514-999-9999"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "nouveau@magasin.com"
        assert data["telephone"] == "514-999-9999"

    def test_get_stores_with_contact_success(self, client, mock_store_service):
        """Test successful retrieval of stores with contact info"""
        # Arrange
        mock_stores = [
            StoreResponse(
                id=1,
                nom="Magasin 1",
                adresse="Adresse 1",
                telephone="514-111-1111",
                email="store1@test.com",
            ),
            StoreResponse(
                id=2,
                nom="Magasin 2",
                adresse="Adresse 2",
                telephone="514-222-2222",
                email=None,
            ),
        ]
        mock_store_service.get_stores_with_contact.return_value = mock_stores

        # Act
        response = client.get("/api/v1/stores/with-contact/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["telephone"] == "514-111-1111"

    def test_unauthorized_access(self, mock_store_service):
        """Test unauthorized access without token"""
        # Arrange
        client = TestClient(app)  # Client without mocked auth

        # Act
        response = client.get("/api/v1/stores")

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "HTTP_ERROR"
