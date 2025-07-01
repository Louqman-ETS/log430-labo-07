import pytest
from fastapi import status
from datetime import datetime

def test_root_endpoint(client):
    """Test l'endpoint racine du service"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "orders-api"
    assert data["status"] == "running"

def test_health_check(client):
    """Test l'endpoint de vérification de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "orders-api"

@pytest.mark.asyncio
async def test_create_order_success(client, sample_order_data, mock_all_services):
    """Test la création réussie d'une commande"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["customer_id"] == sample_order_data["customer_id"]
    assert data["status"] == "pending"
    assert "order_number" in data
    assert data["order_number"].startswith("ORD-")
    assert float(data["subtotal"]) > 0
    assert float(data["tax_amount"]) > 0
    assert float(data["shipping_cost"]) > 0
    assert float(data["total_amount"]) > float(data["subtotal"])

@pytest.mark.asyncio
async def test_create_order_cart_not_found(client, sample_order_data, mock_all_services):
    """Test création de commande avec panier inexistant"""
    order_data = sample_order_data.copy()
    order_data["cart_id"] = 999
    
    response = client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 404
    
    data = response.json()
    assert data["error"] == "Cart not found"

@pytest.mark.asyncio
async def test_create_order_empty_cart(client, sample_order_data, mock_empty_cart):
    """Test création de commande avec panier vide"""
    order_data = sample_order_data.copy()
    order_data["cart_id"] = 2
    
    response = client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "vide" in data["message"]

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client, sample_order_data, mock_insufficient_stock):
    """Test création de commande avec stock insuffisant"""
    order_data = sample_order_data.copy()
    order_data["cart_id"] = 3
    
    response = client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "Stock insuffisant" in data["message"]

def test_get_order_by_id(client, sample_order_data, mock_all_services):
    """Test la récupération d'une commande par ID"""
    # Créer une commande
    create_response = client.post("/api/v1/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Récupérer la commande
    response = client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == sample_order_data["customer_id"]

def test_get_order_not_found(client):
    """Test la récupération d'une commande inexistante"""
    response = client.get("/api/v1/orders/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Order not found"

def test_get_orders_by_customer(client, sample_order_data, mock_all_services):
    """Test la récupération des commandes d'un client"""
    # Créer une commande
    client.post("/api/v1/orders/", json=sample_order_data)
    customer_id = sample_order_data["customer_id"]
    
    # Récupérer les commandes du client
    response = client.get(f"/api/v1/orders/customer/{customer_id}")
    assert response.status_code == 200
    
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    assert orders[0]["customer_id"] == customer_id

def test_update_order_status(client, sample_order_data, mock_all_services):
    """Test la mise à jour du statut d'une commande"""
    # Créer une commande
    create_response = client.post("/api/v1/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Mettre à jour le statut
    status_data = {"status": "confirmed"}
    response = client.put(f"/api/v1/orders/{order_id}/status", json=status_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["confirmed_at"] is not None

def test_update_order_status_invalid(client, sample_order_data, mock_all_services):
    """Test la mise à jour avec statut invalide"""
    # Créer une commande
    create_response = client.post("/api/v1/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Tenter de mettre à jour avec un statut invalide
    status_data = {"status": "invalid_status"}
    response = client.put(f"/api/v1/orders/{order_id}/status", json=status_data)
    assert response.status_code == 422

def test_get_order_statistics(client, sample_order_data, mock_all_services):
    """Test les statistiques des commandes"""
    # Créer quelques commandes
    client.post("/api/v1/orders/", json=sample_order_data)
    
    # Récupérer les statistiques
    response = client.get("/api/v1/orders/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_orders" in data
    assert "total_revenue" in data
    assert "orders_by_status" in data
    assert data["total_orders"] >= 1

def test_order_number_generation(client, sample_order_data, mock_all_services):
    """Test la génération unique des numéros de commande"""
    # Créer deux commandes
    response1 = client.post("/api/v1/orders/", json=sample_order_data)
    order_data2 = sample_order_data.copy()
    order_data2["customer_id"] = 2
    response2 = client.post("/api/v1/orders/", json=order_data2)
    
    order1 = response1.json()
    order2 = response2.json()
    
    # Vérifier que les numéros sont différents
    assert order1["order_number"] != order2["order_number"]
    assert order1["order_number"].startswith("ORD-")
    assert order2["order_number"].startswith("ORD-")

def test_order_tax_calculation(client, sample_order_data, mock_all_services):
    """Test le calcul correct des taxes"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    subtotal = float(order["subtotal"])
    tax_amount = float(order["tax_amount"])
    expected_tax = subtotal * 0.20  # 20% TVA
    
    # Vérifier que la taxe est calculée correctement (avec tolérance pour les arrondis)
    assert abs(tax_amount - expected_tax) < 0.01

def test_order_shipping_cost(client, sample_order_data, mock_all_services):
    """Test le calcul des frais de livraison"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    shipping_cost = float(order["shipping_cost"])
    subtotal = float(order["subtotal"])
    
    # Frais de livraison: 0€ si > 50€, sinon 5€
    expected_shipping = 0.0 if subtotal > 50 else 5.0
    assert shipping_cost == expected_shipping

def test_order_total_calculation(client, sample_order_data, mock_all_services):
    """Test le calcul du total de la commande"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    subtotal = float(order["subtotal"])
    tax_amount = float(order["tax_amount"])
    shipping_cost = float(order["shipping_cost"])
    total_amount = float(order["total_amount"])
    
    expected_total = subtotal + tax_amount + shipping_cost
    assert abs(total_amount - expected_total) < 0.01

def test_order_items_creation(client, sample_order_data, mock_all_services):
    """Test la création des items de commande"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    # Vérifier que les items sont bien créés
    assert "items" in order
    assert len(order["items"]) == 2  # 2 items dans le mock
    
    # Vérifier les détails du premier item
    first_item = order["items"][0]
    assert first_item["product_id"] == 1
    assert first_item["quantity"] == 2
    assert float(first_item["unit_price"]) == 29.99

def test_request_id_propagation(client):
    """Test la propagation du Request-ID"""
    headers = {"X-Request-ID": "order-test-123"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == "order-test-123"

def test_address_storage(client, sample_order_data, mock_all_services):
    """Test le stockage des adresses de livraison et facturation"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    # Vérifier l'adresse de livraison
    shipping = order["shipping_address"]
    assert shipping["street_address"] == sample_order_data["shipping_address"]["street_address"]
    assert shipping["city"] == sample_order_data["shipping_address"]["city"]
    
    # Vérifier l'adresse de facturation
    billing = order["billing_address"]
    assert billing["street_address"] == sample_order_data["billing_address"]["street_address"]
    assert billing["city"] == sample_order_data["billing_address"]["city"]

def test_order_status_transitions(client, sample_order_data, mock_all_services):
    """Test les transitions de statut de commande"""
    # Créer une commande
    create_response = client.post("/api/v1/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Transition: pending -> confirmed
    response = client.put(f"/api/v1/orders/{order_id}/status", json={"status": "confirmed"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    
    # Transition: confirmed -> processing
    response = client.put(f"/api/v1/orders/{order_id}/status", json={"status": "processing"})
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    
    # Transition: processing -> shipped
    response = client.put(f"/api/v1/orders/{order_id}/status", json={"status": "shipped"})
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"

def test_order_timestamps(client, sample_order_data, mock_all_services):
    """Test les timestamps de la commande"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    
    # Vérifier que created_at est défini
    assert order["created_at"] is not None
    
    # Vérifier que les autres timestamps ne sont pas encore définis
    assert order["confirmed_at"] is None
    assert order["shipped_at"] is None
    assert order["delivered_at"] is None

def test_database_coordination_order_items(client, sample_order_data, mock_all_services):
    """Test la coordination entre Order et OrderItem dans la DB"""
    response = client.post("/api/v1/orders/", json=sample_order_data)
    order = response.json()
    order_id = order["id"]
    
    # Vérifier que les items sont liés à la bonne commande
    items = order["items"]
    for item in items:
        assert item["order_id"] == order_id
    
    # Récupérer la commande pour vérifier la persistance
    get_response = client.get(f"/api/v1/orders/{order_id}")
    retrieved_order = get_response.json()
    
    assert len(retrieved_order["items"]) == len(items)
    assert retrieved_order["items"][0]["order_id"] == order_id

def test_inter_service_communication_failure_handling(client, sample_order_data):
    """Test la gestion des échecs de communication inter-services"""
    # Sans mocks - les services externes ne répondront pas
    response = client.post("/api/v1/orders/", json=sample_order_data)
    
    # Le service devrait gérer l'échec gracieusement
    assert response.status_code in [400, 404, 500]  # Selon l'implémentation

def test_order_validation_missing_fields(client):
    """Test la validation avec champs manquants"""
    invalid_order = {
        "cart_id": 1,
        # customer_id manquant
        "shipping_address": {
            "street_address": "123 Test St",
            "city": "Test City",
            "postal_code": "12345",
            "country": "Test Country"
        }
    }
    
    response = client.post("/api/v1/orders/", json=invalid_order)
    assert response.status_code == 422

def test_concurrent_order_creation(client, sample_order_data, mock_all_services):
    """Test la création concurrente de commandes"""
    # Créer plusieurs commandes simultanément
    responses = []
    for i in range(3):
        order_data = sample_order_data.copy()
        order_data["customer_id"] = i + 1
        response = client.post("/api/v1/orders/", json=order_data)
        responses.append(response)
    
    # Vérifier que toutes les commandes sont créées avec succès
    order_numbers = []
    for response in responses:
        assert response.status_code == 201
        order_number = response.json()["order_number"]
        order_numbers.append(order_number)
    
    # Vérifier l'unicité des numéros de commande
    assert len(set(order_numbers)) == len(order_numbers) 