import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.app.api.main import app
from src.app.api.v1 import dependencies


def test_create_product(client: TestClient, db_session: MagicMock):
    product_data = {
        "code": "TEST001",
        "nom": "Test Product",
        "prix": 99.99,
        "categorie_id": 1,
    }

    with patch("src.app.api.v1.crud.create_product") as mock_create:
        mock_create.return_value.id = 1
        mock_create.return_value.code = "TEST001"
        mock_create.return_value.nom = "Test Product"
        mock_create.return_value.description = None
        mock_create.return_value.prix = 99.99
        mock_create.return_value.quantite_stock = 0
        mock_create.return_value.categorie_id = 1

        response = client.post("/api/v1/products", json=product_data)

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == product_data["code"]
        assert data["nom"] == product_data["nom"]
        assert "id" in data
        mock_create.assert_called_once()


def test_read_product(client: TestClient, db_session: MagicMock):
    product_id = 1

    with patch("src.app.api.v1.crud.get_product") as mock_get:
        # We create a new mock object for the return value inside the test
        mock_product = MagicMock()
        mock_product.id = product_id
        mock_product.code = "TEST001"
        mock_product.nom = "Test Product"
        mock_product.description = None
        mock_product.prix = 99.99
        mock_product.quantite_stock = 0
        mock_product.categorie_id = 1
        mock_get.return_value = mock_product

        response = client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        mock_get.assert_called_once_with(db_session, product_id=product_id)


def test_unauthorized_access(client: TestClient):
    # Temporarily remove the auth override for this specific test
    app.dependency_overrides.pop(dependencies.api_token_auth, None)

    response = client.get("/api/v1/products")
    assert response.status_code == 401
    assert "Invalid or missing API Token" in response.json()["message"]

    # Re-add the override for other tests if needed (fixture scope handles this)
    # No need to re-add manually, the fixture setup will run for the next test
