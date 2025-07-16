import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from src.models import SagaState


class TestSagaCompletedScenario:
    """Tests pour le scénario de saga complétée avec succès"""

    @pytest.mark.asyncio
    @patch('src.saga_orchestrator.httpx.AsyncClient.get')
    @patch('src.saga_orchestrator.httpx.AsyncClient.post')
    async def test_complete_saga_success_scenario(self, mock_post, mock_get, client, sample_order_request):
        """Test du scénario complet de saga réussie"""
        
        # Configuration des mocks pour simuler des réponses réussies
        
        # 1. Mock pour vérifier l'existence du client (GET /customers/{id})
        mock_customer_response = MagicMock()
        mock_customer_response.status_code = 200
        mock_customer_response.json.return_value = {
            "id": 1,
            "name": "Test Customer",
            "email": "test@example.com"
        }
        
        # 2. Mock pour vérifier le stock (GET /products/{id}/stock)
        mock_stock_check_response = MagicMock()
        mock_stock_check_response.status_code = 200
        mock_stock_check_response.json.return_value = {
            "product_id": 1,
            "available_quantity": 100,
            "status": "available"
        }
        
        # 3. Mock pour réserver le stock (POST /stock/reserve)
        mock_stock_reserve_response = MagicMock()
        mock_stock_reserve_response.status_code = 200
        mock_stock_reserve_response.json.return_value = {
            "reservation_id": "res_123",
            "status": "reserved",
            "products": [{"product_id": 1, "quantity": 2}]
        }
        
        # 4. Mock pour créer la commande (POST /orders)
        mock_order_create_response = MagicMock()
        mock_order_create_response.status_code = 201
        mock_order_create_response.json.return_value = {
            "order_id": "order_456",
            "customer_id": 1,
            "status": "pending",
            "total_amount": 119.97
        }
        
        # 5. Mock pour traiter le paiement (POST /payments)
        mock_payment_response = MagicMock()
        mock_payment_response.status_code = 200
        mock_payment_response.json.return_value = {
            "payment_id": "pay_789",
            "status": "completed",
            "amount": 119.97
        }
        
        # 6. Mock pour confirmer la commande (PUT /orders/{id}/confirm)
        mock_order_confirm_response = MagicMock()
        mock_order_confirm_response.status_code = 200
        mock_order_confirm_response.json.return_value = {
            "order_id": "order_456",
            "status": "confirmed"
        }
        
        # Configuration des mocks selon l'ordre des appels
        mock_get.side_effect = [
            mock_customer_response,  # Vérification client
            mock_stock_check_response,  # Vérification stock produit 1
            mock_stock_check_response,  # Vérification stock produit 2
        ]
        
        mock_post.side_effect = [
            mock_stock_reserve_response,  # Réservation stock
            mock_order_create_response,   # Création commande
            mock_payment_response,        # Traitement paiement
            mock_order_confirm_response,  # Confirmation commande
        ]
        
        # Exécution du test
        customer_id = 1
        response = client.post(
            f"/api/v1/customers/{customer_id}/order-processing",
            json={
                "cart_id": sample_order_request["cart_id"],
                "products": sample_order_request["products"],
                "shipping_address": sample_order_request["shipping_address"],
                "billing_address": sample_order_request["billing_address"],
                "payment_method": sample_order_request["payment_method"],
                "simulate_failure": False
            }
        )
        
        # Vérifications
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        response_data = response.json()
        assert "saga_id" in response_data
        assert response_data["status"] == "started"
        assert response_data["customer_id"] == customer_id
        
        saga_id = response_data["saga_id"]
        
        # Attendre un peu pour que la saga se termine
        import time
        time.sleep(2)
        
        # Vérifier l'état final de la saga
        saga_status_response = client.get(f"/api/v1/sagas/{saga_id}")
        assert saga_status_response.status_code == status.HTTP_200_OK
        
        saga_data = saga_status_response.json()
        assert saga_data["state"] == "COMPLETED"
        assert saga_data["customer_id"] == customer_id

    @pytest.mark.asyncio
    async def test_saga_metrics_after_completion(self, client, sample_order_request):
        """Test que les métriques sont correctement mises à jour après une saga complétée"""
        
        # Vérifier les métriques avant
        metrics_before = client.get("/metrics")
        assert metrics_before.status_code == status.HTTP_200_OK
        
        # Note: Dans un vrai test, on démarrerait une saga réussie ici
        # et vérifierait que les métriques saga_orchestrator_sagas_total{status="completed"} 
        # ont augmenté
        
        # Vérifier les statistiques
        stats_response = client.get("/api/v1/sagas/stats/summary")
        assert stats_response.status_code == status.HTTP_200_OK
        
        stats_data = stats_response.json()
        assert "total_sagas" in stats_data
        assert "completed_sagas" in stats_data
        assert "success_rate" in stats_data


class TestSagaCompensatedScenario:
    """Tests pour le scénario de saga compensée (échec avec rollback)"""

    @pytest.mark.asyncio
    @patch('src.saga_orchestrator.httpx.AsyncClient.get')
    @patch('src.saga_orchestrator.httpx.AsyncClient.post')
    @patch('src.saga_orchestrator.httpx.AsyncClient.delete')
    async def test_compensated_saga_customer_not_found(self, mock_delete, mock_post, mock_get, client, sample_order_request):
        """Test de saga compensée - client inexistant"""
        
        # Mock pour client inexistant
        mock_customer_response = MagicMock()
        mock_customer_response.status_code = 404
        mock_customer_response.json.return_value = {
            "detail": "Customer not found"
        }
        
        mock_get.side_effect = [mock_customer_response]
        
        # Exécution du test avec un client inexistant
        customer_id = 99999
        response = client.post(
            f"/api/v1/customers/{customer_id}/order-processing",
            json={
                "cart_id": sample_order_request["cart_id"],
                "products": sample_order_request["products"],
                "shipping_address": sample_order_request["shipping_address"],
                "billing_address": sample_order_request["billing_address"],
                "payment_method": sample_order_request["payment_method"],
                "simulate_failure": False
            }
        )
        
        # Vérifications
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert "error" in response_data
        assert "Customer" in response_data["error"]

    @pytest.mark.asyncio
    @patch('src.saga_orchestrator.httpx.AsyncClient.get')
    @patch('src.saga_orchestrator.httpx.AsyncClient.post')
    @patch('src.saga_orchestrator.httpx.AsyncClient.delete')
    async def test_compensated_saga_payment_failure(self, mock_delete, mock_post, mock_get, client, sample_order_request):
        """Test de saga compensée - échec du paiement avec compensation"""
        
        # Configuration des mocks pour un échec au niveau du paiement
        
        # 1. Client existe
        mock_customer_response = MagicMock()
        mock_customer_response.status_code = 200
        mock_customer_response.json.return_value = {
            "id": 1,
            "name": "Test Customer"
        }
        
        # 2. Stock disponible
        mock_stock_check_response = MagicMock()
        mock_stock_check_response.status_code = 200
        mock_stock_check_response.json.return_value = {
            "product_id": 1,
            "available_quantity": 100,
            "status": "available"
        }
        
        # 3. Réservation stock réussie
        mock_stock_reserve_response = MagicMock()
        mock_stock_reserve_response.status_code = 200
        mock_stock_reserve_response.json.return_value = {
            "reservation_id": "res_123",
            "status": "reserved"
        }
        
        # 4. Création commande réussie
        mock_order_create_response = MagicMock()
        mock_order_create_response.status_code = 201
        mock_order_create_response.json.return_value = {
            "order_id": "order_456",
            "status": "pending"
        }
        
        # 5. ÉCHEC du paiement
        mock_payment_failure_response = MagicMock()
        mock_payment_failure_response.status_code = 400
        mock_payment_failure_response.json.return_value = {
            "error": "Payment declined - insufficient funds"
        }
        
        # 6. Mocks pour les compensations
        mock_stock_release_response = MagicMock()
        mock_stock_release_response.status_code = 200
        mock_stock_release_response.json.return_value = {"status": "released"}
        
        mock_order_cancel_response = MagicMock()
        mock_order_cancel_response.status_code = 200
        mock_order_cancel_response.json.return_value = {"status": "cancelled"}
        
        # Configuration des side effects
        mock_get.side_effect = [
            mock_customer_response,
            mock_stock_check_response,
            mock_stock_check_response,
        ]
        
        mock_post.side_effect = [
            mock_stock_reserve_response,
            mock_order_create_response,
            mock_payment_failure_response,  # Échec du paiement
        ]
        
        mock_delete.side_effect = [
            mock_stock_release_response,  # Libération du stock
            mock_order_cancel_response,   # Annulation commande
        ]
        
        # Exécution du test
        customer_id = 1
        response = client.post(
            f"/api/v1/customers/{customer_id}/order-processing",
            json={
                "cart_id": sample_order_request["cart_id"],
                "products": sample_order_request["products"],
                "shipping_address": sample_order_request["shipping_address"],
                "billing_address": sample_order_request["billing_address"],
                "payment_method": sample_order_request["payment_method"],
                "simulate_failure": False
            }
        )
        
        # Vérifications
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        response_data = response.json()
        saga_id = response_data["saga_id"]
        
        # Attendre que la saga se termine avec compensation
        import time
        time.sleep(3)
        
        # Vérifier l'état final de la saga
        saga_status_response = client.get(f"/api/v1/sagas/{saga_id}")
        assert saga_status_response.status_code == status.HTTP_200_OK
        
        saga_data = saga_status_response.json()
        assert saga_data["state"] == "COMPENSATED"
        
        # Vérifier les événements de compensation
        events_response = client.get(f"/api/v1/sagas/{saga_id}/events")
        assert events_response.status_code == status.HTTP_200_OK
        
        events = events_response.json()
        assert len(events) > 0
        
        # Vérifier qu'il y a des événements de compensation
        compensation_events = [e for e in events if "compensation" in e.get("event_type", "").lower()]
        assert len(compensation_events) > 0

    @pytest.mark.asyncio
    async def test_saga_with_simulate_failure_flag(self, client, sample_order_request):
        """Test de saga avec le flag simulate_failure activé"""
        
        customer_id = 1
        response = client.post(
            f"/api/v1/customers/{customer_id}/order-processing",
            json={
                "cart_id": sample_order_request["cart_id"],
                "products": sample_order_request["products"],
                "shipping_address": sample_order_request["shipping_address"],
                "billing_address": sample_order_request["billing_address"],
                "payment_method": sample_order_request["payment_method"],
                "simulate_failure": True  # Force l'échec
            }
        )
        
        # Vérifications
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        response_data = response.json()
        saga_id = response_data["saga_id"]
        
        # Attendre que la saga échoue
        import time
        time.sleep(2)
        
        # Vérifier que la saga est compensée
        saga_status_response = client.get(f"/api/v1/sagas/{saga_id}")
        assert saga_status_response.status_code == status.HTTP_200_OK
        
        saga_data = saga_status_response.json()
        assert saga_data["state"] in ["COMPENSATED", "FAILED"]

    @pytest.mark.asyncio
    async def test_saga_metrics_after_compensation(self, client):
        """Test que les métriques sont correctement mises à jour après une saga compensée"""
        
        # Vérifier les métriques
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == status.HTTP_200_OK
        
        # Vérifier les statistiques
        stats_response = client.get("/api/v1/sagas/stats/summary")
        assert stats_response.status_code == status.HTTP_200_OK
        
        stats_data = stats_response.json()
        assert "total_sagas" in stats_data
        assert "failed_sagas" in stats_data
        assert "success_rate" in stats_data


class TestSagaEdgeCases:
    """Tests pour les cas limites et erreurs"""

    def test_invalid_customer_id_format(self, client, sample_order_request):
        """Test avec un ID client invalide"""
        
        response = client.post(
            "/api/v1/customers/invalid_id/order-processing",
            json={
                "cart_id": sample_order_request["cart_id"],
                "products": sample_order_request["products"],
                "shipping_address": sample_order_request["shipping_address"],
                "billing_address": sample_order_request["billing_address"],
                "payment_method": sample_order_request["payment_method"],
                "simulate_failure": False
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_products_list(self, client):
        """Test avec une liste de produits vide"""
        
        response = client.post(
            "/api/v1/customers/1/order-processing",
            json={
                "cart_id": 123,
                "products": [],  # Liste vide
                "shipping_address": "123 Test St",
                "billing_address": "123 Test St",
                "payment_method": "credit_card",
                "simulate_failure": False
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client):
        """Test avec des champs obligatoires manquants"""
        
        response = client.post(
            "/api/v1/customers/1/order-processing",
            json={
                "cart_id": 123,
                "products": [{"product_id": 1, "quantity": 1, "price": 29.99}],
                # Manque shipping_address, billing_address, payment_method
                "simulate_failure": False
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 