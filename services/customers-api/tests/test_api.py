import pytest
import json
from fastapi import status

def test_root_endpoint(client):
    """Test l'endpoint racine du service"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "customers-api"
    assert data["status"] == "running"

def test_health_check(client):
    """Test l'endpoint de vérification de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "customers-api"

def test_register_customer(client, sample_customer_data):
    """Test l'inscription d'un nouveau client"""
    response = client.post("/api/v1/customers/register", json=sample_customer_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "customer" in data
    assert "token" in data
    assert data["customer"]["email"] == sample_customer_data["email"]
    assert data["customer"]["first_name"] == sample_customer_data["first_name"]
    assert data["token"]["token_type"] == "bearer"

def test_register_duplicate_email(client, sample_customer_data):
    """Test l'inscription avec un email déjà utilisé"""
    # Première inscription
    client.post("/api/v1/customers/register", json=sample_customer_data)
    
    # Deuxième inscription avec le même email
    response = client.post("/api/v1/customers/register", json=sample_customer_data)
    assert response.status_code == 409
    data = response.json()
    assert data["error"] == "Email already registered"

def test_login_customer(client, sample_customer_data):
    """Test la connexion d'un client"""
    # Inscription préalable
    client.post("/api/v1/customers/register", json=sample_customer_data)
    
    # Connexion
    login_data = {
        "email": sample_customer_data["email"],
        "password": sample_customer_data["password"]
    }
    response = client.post("/api/v1/customers/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "customer" in data
    assert "token" in data
    assert data["customer"]["email"] == sample_customer_data["email"]

def test_login_invalid_credentials(client):
    """Test la connexion avec des identifiants invalides"""
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/customers/login", json=login_data)
    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Invalid credentials"

def test_get_customer_profile(client, sample_customer_data):
    """Test la récupération du profil client"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Récupération du profil
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/customers/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == sample_customer_data["email"]
    assert data["first_name"] == sample_customer_data["first_name"]

def test_update_customer_profile(client, sample_customer_data):
    """Test la mise à jour du profil client"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Mise à jour du profil
    update_data = {"first_name": "Updated", "last_name": "Name"}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("/api/v1/customers/me", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"

def test_create_address(client, sample_customer_data, sample_address_data):
    """Test la création d'une adresse client"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Création d'une adresse
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/customers/me/addresses/", json=sample_address_data, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["type"] == sample_address_data["type"]
    assert data["city"] == sample_address_data["city"]
    assert data["is_default"] == True

def test_get_customer_addresses(client, sample_customer_data, sample_address_data):
    """Test la récupération des adresses d'un client"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Création d'une adresse
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/customers/me/addresses/", json=sample_address_data, headers=headers)
    
    # Récupération des adresses
    response = client.get("/api/v1/customers/me/addresses/", headers=headers)
    assert response.status_code == 200
    
    addresses = response.json()
    assert len(addresses) == 1
    assert addresses[0]["type"] == sample_address_data["type"]

def test_unauthorized_access(client):
    """Test l'accès non autorisé aux endpoints protégés"""
    response = client.get("/api/v1/customers/me")
    assert response.status_code == 403

def test_invalid_token_access(client):
    """Test l'accès avec un token invalide"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/customers/me", headers=headers)
    assert response.status_code == 401

def test_change_password(client, sample_customer_data):
    """Test le changement de mot de passe"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Changement de mot de passe
    password_data = {
        "current_password": sample_customer_data["password"],
        "new_password": "newpassword123"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/customers/me/change-password", json=password_data, headers=headers)
    assert response.status_code == 200

def test_get_customer_stats(client, sample_customer_data):
    """Test les statistiques des clients"""
    # Créer quelques clients
    client.post("/api/v1/customers/register", json=sample_customer_data)
    
    # Récupérer les statistiques
    response = client.get("/api/v1/customers/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_customers" in data
    assert "active_customers" in data
    assert data["total_customers"] >= 1

def test_request_id_header(client):
    """Test que le Request-ID est bien propagé"""
    headers = {"X-Request-ID": "test-request-123"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == "test-request-123"

def test_address_validation_errors(client, sample_customer_data):
    """Test les erreurs de validation pour les adresses"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Test avec une adresse invalide (postal_code trop court)
    invalid_address = {
        "type": "shipping",
        "street_address": "123 Test St",
        "city": "Test City",
        "postal_code": "123",  # Trop court
        "country": "France"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/customers/me/addresses/", json=invalid_address, headers=headers)
    assert response.status_code == 422

def test_customer_deactivation(client, sample_customer_data):
    """Test la désactivation d'un compte client"""
    # Inscription et récupération du token
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    
    # Désactivation du compte
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/v1/customers/me", headers=headers)
    assert response.status_code == 200
    
    # Vérifier que l'accès est maintenant interdit
    response = client.get("/api/v1/customers/me", headers=headers)
    assert response.status_code == 404  # Customer not found car désactivé

def test_database_coordination(client, sample_customer_data, sample_address_data):
    """Test la coordination entre Customer et Address dans la DB"""
    # Inscription
    register_response = client.post("/api/v1/customers/register", json=sample_customer_data)
    token = register_response.json()["token"]["access_token"]
    customer_id = register_response.json()["customer"]["id"]
    
    # Création d'une adresse
    headers = {"Authorization": f"Bearer {token}"}
    address_response = client.post("/api/v1/customers/me/addresses/", json=sample_address_data, headers=headers)
    address_data = address_response.json()
    
    # Vérifier que l'adresse est liée au bon client
    assert address_data["customer_id"] == customer_id
    
    # Vérifier la récupération cohérente
    addresses_response = client.get("/api/v1/customers/me/addresses/", headers=headers)
    addresses = addresses_response.json()
    
    assert len(addresses) == 1
    assert addresses[0]["customer_id"] == customer_id
    assert addresses[0]["id"] == address_data["id"] 