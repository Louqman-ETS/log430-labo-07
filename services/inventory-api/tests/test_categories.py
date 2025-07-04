import pytest
from unittest.mock import patch
from fastapi import status

class TestCategories:
    def test_get_categories_success(self, client):
        response = client.get("/api/v1/categories/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Il y a 6 catégories dans la base d'init
        assert isinstance(data, list)
        assert len(data) == 6
        assert any(cat["nom"] == "Électronique" for cat in data)

    def test_get_category_by_id_success(self, client):
        response = client.get("/api/v1/categories/2")  # 2 = Électronique dans init_db
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 2
        assert data["nom"] == "Électronique"

    def test_get_category_by_id_not_found(self, client):
        response = client.get("/api/v1/categories/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_category_success(self, client):
        # Utiliser un nom unique pour éviter la contrainte UNIQUE
        category_data = {
            "nom": "TestCatUnique",
            "description": "Catégorie de test unique"
        }
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nom"] == "TestCatUnique"

    def test_create_category_invalid_data(self, client):
        category_data = {"nom": ""}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_category_success(self, client):
        update_data = {"nom": "Catégorie modifiée"}
        response = client.put("/api/v1/categories/2", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nom"] == "Catégorie modifiée"

    def test_update_category_not_found(self, client):
        update_data = {"nom": "Catégorie modifiée"}
        response = client.put("/api/v1/categories/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_success(self, client):
        # Créer une catégorie temporaire pour la supprimer sans erreur d'intégrité
        category_data = {"nom": "TempDeleteCat", "description": "Temporaire"}
        create_resp = client.post("/api/v1/categories/", json=category_data)
        assert create_resp.status_code == status.HTTP_201_CREATED
        cat_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/categories/{cat_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_category_not_found(self, client):
        response = client.delete("/api/v1/categories/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND 