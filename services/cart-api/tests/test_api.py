import pytest
from fastapi import status

def test_root_endpoint(client):
    """Test l'endpoint racine du service"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "cart-api"
    assert data["status"] == "running"

def test_health_check(client):
    """Test l'endpoint de vérification de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cart-api"

def test_create_cart_for_customer(client, sample_cart_data):
    """Test la création d'un panier pour un client"""
    response = client.post("/api/v1/carts/", json=sample_cart_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["customer_id"] == sample_cart_data["customer_id"]
    assert data["is_active"] == True
    assert data["total_items"] == 0
    assert data["total_price"] == 0

def test_create_cart_for_guest(client, sample_guest_cart_data):
    """Test la création d'un panier pour un invité"""
    response = client.post("/api/v1/carts/", json=sample_guest_cart_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["session_id"] == sample_guest_cart_data["session_id"]
    assert data["customer_id"] is None
    assert data["is_active"] == True

def test_get_cart_by_customer(client, sample_cart_data):
    """Test la récupération d'un panier par client"""
    # Créer un panier
    create_response = client.post("/api/v1/carts/", json=sample_cart_data)
    customer_id = sample_cart_data["customer_id"]
    
    # Récupérer le panier
    response = client.get(f"/api/v1/carts/customer/{customer_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["customer_id"] == customer_id

def test_get_cart_by_session(client, sample_guest_cart_data):
    """Test la récupération d'un panier par session"""
    # Créer un panier invité
    create_response = client.post("/api/v1/carts/", json=sample_guest_cart_data)
    session_id = sample_guest_cart_data["session_id"]
    
    # Récupérer le panier
    response = client.get(f"/api/v1/carts/session/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id

@pytest.mark.asyncio
async def test_add_item_to_cart(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test l'ajout d'un article au panier"""
    # Créer un panier
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Ajouter un article
    item_data = {"product_id": 1, "quantity": 2}
    response = client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["product_id"] == 1
    assert data["quantity"] == 2
    assert float(data["unit_price"]) == 29.99

@pytest.mark.asyncio
async def test_add_item_insufficient_stock(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test l'ajout d'un article avec stock insuffisant"""
    # Créer un panier
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Tenter d'ajouter un article avec quantité excessive (produit 2 a seulement 5 en stock)
    item_data = {"product_id": 2, "quantity": 10}
    response = client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "Stock insuffisant" in data["message"]

@pytest.mark.asyncio
async def test_add_nonexistent_product(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test l'ajout d'un produit inexistant"""
    # Créer un panier
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Tenter d'ajouter un produit inexistant
    item_data = {"product_id": 999, "quantity": 1}
    response = client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "non trouvé" in data["message"]

@pytest.mark.asyncio
async def test_update_cart_item(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test la mise à jour d'un article du panier"""
    # Créer un panier et ajouter un article
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    item_data = {"product_id": 1, "quantity": 2}
    client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    
    # Mettre à jour la quantité
    update_data = {"quantity": 5}
    response = client.put(f"/api/v1/carts/{cart_id}/items/1", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["quantity"] == 5

def test_remove_item_from_cart(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test la suppression d'un article du panier"""
    # Créer un panier et ajouter un article
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    item_data = {"product_id": 1, "quantity": 2}
    client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    
    # Supprimer l'article
    response = client.delete(f"/api/v1/carts/{cart_id}/items/1")
    assert response.status_code == 200
    
    data = response.json()
    assert "retiré" in data["message"]

def test_clear_cart(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test le vidage d'un panier"""
    # Créer un panier et ajouter des articles
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    item_data = {"product_id": 1, "quantity": 2}
    client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    
    # Vider le panier
    response = client.delete(f"/api/v1/carts/{cart_id}/clear")
    assert response.status_code == 200
    
    data = response.json()
    assert "vidé" in data["message"]

@pytest.mark.asyncio
async def test_validate_cart(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test la validation d'un panier"""
    # Créer un panier et ajouter un article
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    item_data = {"product_id": 1, "quantity": 2}
    client.post(f"/api/v1/carts/{cart_id}/items", json=item_data)
    
    # Valider le panier
    response = client.post(f"/api/v1/carts/{cart_id}/validate")
    assert response.status_code == 200
    
    data = response.json()
    assert data["is_valid"] == True
    assert float(data["total_price"]) > 0

def test_get_cart_statistics(client, sample_cart_data):
    """Test les statistiques des paniers"""
    # Créer quelques paniers
    client.post("/api/v1/carts/", json=sample_cart_data)
    
    # Récupérer les statistiques
    response = client.get("/api/v1/carts/stats/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_active_carts" in data
    assert "total_items_in_carts" in data
    assert data["total_active_carts"] >= 1

def test_cart_not_found(client):
    """Test l'accès à un panier inexistant"""
    response = client.get("/api/v1/carts/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Cart not found"

def test_item_not_found_for_update(client, sample_cart_data):
    """Test la mise à jour d'un article inexistant"""
    # Créer un panier vide
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Tenter de mettre à jour un article inexistant
    update_data = {"quantity": 5}
    response = client.put(f"/api/v1/carts/{cart_id}/items/999", json=update_data)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Cart item not found"

def test_item_not_found_for_removal(client, sample_cart_data):
    """Test la suppression d'un article inexistant"""
    # Créer un panier vide
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Tenter de supprimer un article inexistant
    response = client.delete(f"/api/v1/carts/{cart_id}/items/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Cart item not found"

def test_request_id_propagation(client):
    """Test la propagation du Request-ID"""
    headers = {"X-Request-ID": "cart-test-123"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == "cart-test-123"

@pytest.mark.asyncio
async def test_cart_total_calculation(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test le calcul correct des totaux du panier"""
    # Créer un panier
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Ajouter plusieurs articles
    client.post(f"/api/v1/carts/{cart_id}/items", json={"product_id": 1, "quantity": 2})  # 2 * 29.99 = 59.98
    client.post(f"/api/v1/carts/{cart_id}/items", json={"product_id": 2, "quantity": 1})  # 1 * 19.99 = 19.99
    
    # Récupérer le panier pour vérifier les totaux
    response = client.get(f"/api/v1/carts/{cart_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_items"] == 3  # 2 + 1
    expected_total = 59.98 + 19.99  # 79.97
    assert abs(float(data["total_price"]) - expected_total) < 0.01

def test_cart_database_coordination(client, sample_cart_data, sample_guest_cart_data):
    """Test la coordination entre les tables Cart et CartItem"""
    # Créer deux paniers (client et invité)
    customer_cart = client.post("/api/v1/carts/", json=sample_cart_data)
    guest_cart = client.post("/api/v1/carts/", json=sample_guest_cart_data)
    
    customer_cart_id = customer_cart.json()["id"]
    guest_cart_id = guest_cart.json()["id"]
    
    # Vérifier que les paniers sont distincts
    assert customer_cart_id != guest_cart_id
    
    # Vérifier les données du panier client
    customer_data = customer_cart.json()
    assert customer_data["customer_id"] == 1
    assert customer_data["session_id"] is None
    
    # Vérifier les données du panier invité
    guest_data = guest_cart.json()
    assert guest_data["customer_id"] is None
    assert guest_data["session_id"] == "guest-session-123"

@pytest.mark.asyncio
async def test_concurrent_cart_operations(client, sample_cart_data, mock_products_api, mock_stock_api):
    """Test les opérations concurrentes sur le panier"""
    # Créer un panier
    cart_response = client.post("/api/v1/carts/", json=sample_cart_data)
    cart_id = cart_response.json()["id"]
    
    # Ajouter le même produit plusieurs fois (simule concurrence)
    client.post(f"/api/v1/carts/{cart_id}/items", json={"product_id": 1, "quantity": 1})
    client.post(f"/api/v1/carts/{cart_id}/items", json={"product_id": 1, "quantity": 2})
    
    # Récupérer le panier
    response = client.get(f"/api/v1/carts/{cart_id}")
    cart_data = response.json()
    
    # Doit avoir un seul article avec quantité combinée
    assert len(cart_data["items"]) == 1
    assert cart_data["items"][0]["quantity"] == 3  # 1 + 2 