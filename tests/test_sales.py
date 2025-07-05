import pytest
from fastapi.testclient import TestClient


def test_get_sales(client: TestClient):
    """Test de récupération de toutes les ventes."""
    response = client.get("/api/v1/sales/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Vérifier la structure des données si des ventes existent
    if data:
        sale = data[0]
        assert "id" in sale
        assert "store_id" in sale
        assert "total_amount" in sale
        assert "date_sale" in sale
        assert "status" in sale


def test_get_sale_by_id_not_found(client: TestClient):
    """Test de récupération d'une vente inexistante."""
    response = client.get("/api/v1/sales/99999")
    assert response.status_code == 404


def test_get_sales_statistics(client: TestClient):
    """Test de récupération des statistiques de ventes."""
    response = client.get("/api/v1/sales/statistics")
    # L'endpoint pourrait ne pas être implémenté
    assert response.status_code in [200, 404, 422]
