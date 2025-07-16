import pytest
from fastapi import status


class TestBasicAPI:
    """Tests de base pour l'API"""

    def test_root_endpoint(self, client):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Saga Orchestrator API is running"
        assert data["service"] == "saga-orchestrator"
        assert "features" in data

    def test_health_check(self, client):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "saga-orchestrator"

    def test_metrics_endpoint(self, client):
        """Test de l'endpoint des métriques"""
        response = client.get("/metrics")
        assert response.status_code == status.HTTP_200_OK
        # Le contenu devrait être au format Prometheus
        assert "saga_orchestrator" in response.text

    def test_docs_endpoint(self, client):
        """Test de l'endpoint de documentation"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_endpoint(self, client):
        """Test de l'endpoint OpenAPI"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["info"]["title"] == "🔄 Saga Orchestrator API"


class TestSagaAPI:
    """Tests pour l'API des sagas"""

    def test_get_empty_sagas_list(self, client):
        """Test de récupération d'une liste vide de sagas"""
        response = client.get("/api/v1/sagas/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_get_saga_not_found(self, client):
        """Test de récupération d'une saga inexistante"""
        response = client.get("/api/v1/sagas/nonexistent-saga-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_saga_events_not_found(self, client):
        """Test de récupération d'événements pour une saga inexistante"""
        response = client.get("/api/v1/sagas/nonexistent-saga-id/events")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []  # Liste vide pour saga inexistante

    def test_get_saga_statistics(self, client):
        """Test de récupération des statistiques"""
        response = client.get("/api/v1/sagas/stats/summary")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_sagas" in data
        assert "pending_sagas" in data
        assert "completed_sagas" in data
        assert "failed_sagas" in data
        assert "success_rate" in data

    @pytest.mark.asyncio
    async def test_start_saga_missing_fields(self, client):
        """Test de démarrage de saga avec des champs manquants"""
        incomplete_request = {
            "customer_id": 1,
            # Manque products, shipping_address, billing_address
        }
        response = client.post("/api/v1/sagas/order-processing", json=incomplete_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_start_saga_invalid_data(self, client):
        """Test de démarrage de saga avec des données invalides"""
        invalid_request = {
            "customer_id": "invalid",  # Devrait être un int
            "products": [],
            "shipping_address": "",
            "billing_address": ""
        }
        response = client.post("/api/v1/sagas/order-processing", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 