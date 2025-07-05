import pytest
from fastapi import status


class TestProducts:

    def test_get_product_by_id_not_found(self, client):
        response = client.get("/api/v1/products/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_product_success(self, client):
        product_data = {
            "nom": "ProduitTestUnique",
            "description": "Produit de test unique",
            "prix": 10.99,
            "categorie_id": 2,  # Électronique
            "code": "TEST-001",
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nom"] == "ProduitTestUnique"

    def test_create_product_invalid_data(self, client):
        product_data = {"nom": "", "prix": -1}
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_product_not_found(self, client):
        update_data = {"nom": "ProduitModifié"}
        response = client.put("/api/v1/products/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_success(self, client):
        # Créer un produit temporaire pour la suppression
        product_data = {
            "nom": "TempDeleteProd",
            "description": "Temporaire",
            "prix": 1.0,
            "categorie_id": 2,
            "code": "TMP-DEL",
        }
        create_resp = client.post("/api/v1/products/", json=product_data)
        assert create_resp.status_code == status.HTTP_201_CREATED
        prod_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/products/{prod_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_product_not_found(self, client):
        response = client.delete("/api/v1/products/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
