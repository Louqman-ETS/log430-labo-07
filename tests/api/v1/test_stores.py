import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


def test_create_store(client: TestClient, db_session: MagicMock):
    store_data = {"nom": "Test Store", "adresse": "123 Test St"}

    with patch("src.app.api.v1.crud.create_store") as mock_create:
        mock_store = MagicMock()
        mock_store.id = 1
        mock_store.nom = "Test Store"
        mock_store.adresse = "123 Test St"
        mock_store.telephone = None
        mock_store.email = None
        mock_create.return_value = mock_store

        response = client.post("/api/v1/stores", json=store_data)

        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == store_data["nom"]
        assert data["adresse"] == store_data["adresse"]
        assert "id" in data
        mock_create.assert_called_once()


def test_read_store(client: TestClient, db_session: MagicMock):
    store_id = 1

    with patch("src.app.api.v1.crud.get_store") as mock_get:
        mock_store = MagicMock()
        mock_store.id = store_id
        mock_store.nom = "Test Store"
        mock_store.adresse = "123 Test St"
        mock_store.telephone = None
        mock_store.email = None
        mock_get.return_value = mock_store

        response = client.get(f"/api/v1/stores/{store_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == store_id
        assert data["nom"] == "Test Store"
        mock_get.assert_called_once_with(db_session, store_id=store_id)


def test_read_stores_paginated(client: TestClient, db_session: MagicMock):
    with patch("src.app.api.v1.crud.get_stores") as mock_get_stores, patch(
        "src.app.api.v1.crud.get_stores_count"
    ) as mock_count:

        mock_store = MagicMock()
        mock_store.id = 1
        mock_store.nom = "Test Store"
        mock_store.adresse = "123 Test St"
        mock_store.telephone = None
        mock_store.email = None

        mock_get_stores.return_value = [mock_store]
        mock_count.return_value = 1

        response = client.get("/api/v1/stores?page=1&size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["size"] == 10
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == 1
        mock_get_stores.assert_called_once_with(db_session, skip=0, limit=10)
        mock_count.assert_called_once_with(db_session)
