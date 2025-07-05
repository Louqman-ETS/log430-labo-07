#!/usr/bin/env python3
"""
Script de génération de données de test pour tester la coordination entre microservices
"""

import requests
import json
import time
from faker import Faker
import random

fake = Faker("fr_FR")

# URLs des services
SERVICES = {
    "products": "http://localhost:8001",
    "stores": "http://localhost:8002",
    "sales": "http://localhost:8003",
    "stock": "http://localhost:8004",
    "reporting": "http://localhost:8005",
    "customers": "http://localhost:8006",
    "cart": "http://localhost:8007",
    "orders": "http://localhost:8008",
}


def wait_for_services():
    """Attendre que tous les services soient prêts"""
    print("🔄 Vérification de l'état des services...")
    for name, url in SERVICES.items():
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} service ready")
                    break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    print(f"❌ {name} service not ready after {max_retries} attempts")
                    return False
                time.sleep(2)
    return True


def create_categories():
    """Créer des catégories de produits"""
    print("\n📁 Création des catégories...")
    categories = [
        {"name": "Électronique", "description": "Produits électroniques"},
        {"name": "Vêtements", "description": "Vêtements et accessoires"},
        {"name": "Maison", "description": "Articles pour la maison"},
        {"name": "Sports", "description": "Équipements sportifs"},
        {"name": "Livres", "description": "Livres et magazines"},
    ]

    created_categories = []
    for cat in categories:
        try:
            response = requests.post(
                f"{SERVICES['products']}/api/v1/categories", json=cat
            )
            if response.status_code == 201:
                created_cat = response.json()
                created_categories.append(created_cat)
                print(
                    f"✅ Catégorie créée: {created_cat['name']} (ID: {created_cat['id']})"
                )
            else:
                print(f"❌ Erreur création catégorie {cat['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Erreur: {e}")

    return created_categories


def create_products(categories):
    """Créer des produits"""
    print("\n📦 Création des produits...")
    products_data = [
        {
            "name": "iPhone 15",
            "description": "Smartphone Apple",
            "price": 899.99,
            "category": "Électronique",
        },
        {
            "name": "MacBook Pro",
            "description": "Ordinateur portable",
            "price": 1999.99,
            "category": "Électronique",
        },
        {
            "name": "T-shirt Nike",
            "description": "T-shirt de sport",
            "price": 29.99,
            "category": "Vêtements",
        },
        {
            "name": "Jean Levi's",
            "description": "Jean classique",
            "price": 79.99,
            "category": "Vêtements",
        },
        {
            "name": "Cafetière",
            "description": "Cafetière électrique",
            "price": 49.99,
            "category": "Maison",
        },
        {
            "name": "Ballon de foot",
            "description": "Ballon officiel",
            "price": 19.99,
            "category": "Sports",
        },
        {
            "name": "Livre Python",
            "description": "Guide de programmation",
            "price": 39.99,
            "category": "Livres",
        },
    ]

    # Mapper les catégories par nom
    cat_map = {cat["name"]: cat["id"] for cat in categories}

    created_products = []
    for prod in products_data:
        product = {
            "name": prod["name"],
            "description": prod["description"],
            "price": prod["price"],
            "category_id": cat_map.get(prod["category"], categories[0]["id"]),
        }

        try:
            response = requests.post(
                f"{SERVICES['products']}/api/v1/products", json=product
            )
            if response.status_code == 201:
                created_prod = response.json()
                created_products.append(created_prod)
                print(
                    f"✅ Produit créé: {created_prod['name']} (ID: {created_prod['id']}) - {created_prod['price']}€"
                )
            else:
                print(f"❌ Erreur création produit {prod['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Erreur: {e}")

    return created_products


def create_stores():
    """Créer des magasins"""
    print("\n🏪 Création des magasins...")
    stores_data = [
        {
            "name": "Store Paris Centre",
            "address": "123 Rue de Rivoli, Paris",
            "city": "Paris",
        },
        {
            "name": "Store Lyon",
            "address": "45 Rue de la République, Lyon",
            "city": "Lyon",
        },
        {
            "name": "Store Marseille",
            "address": "78 Cours Belsunce, Marseille",
            "city": "Marseille",
        },
    ]

    created_stores = []
    for store in stores_data:
        try:
            response = requests.post(f"{SERVICES['stores']}/api/v1/stores", json=store)
            if response.status_code == 201:
                created_store = response.json()
                created_stores.append(created_store)
                print(
                    f"✅ Magasin créé: {created_store['name']} (ID: {created_store['id']})"
                )
            else:
                print(f"❌ Erreur création magasin {store['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Erreur: {e}")

    return created_stores


def create_stock_entries(products, stores):
    """Créer des entrées de stock"""
    print("\n📊 Création des stocks...")

    for product in products:
        for store in stores:
            quantity = random.randint(10, 100)
            stock_entry = {
                "product_id": product["id"],
                "store_id": store["id"],
                "quantity": quantity,
                "reserved_quantity": 0,
            }

            try:
                response = requests.post(
                    f"{SERVICES['stock']}/api/v1/stock", json=stock_entry
                )
                if response.status_code == 201:
                    print(
                        f"✅ Stock créé: {product['name']} à {store['name']} - {quantity} unités"
                    )
                else:
                    print(f"❌ Erreur création stock: {response.text}")
            except Exception as e:
                print(f"❌ Erreur: {e}")


def create_customers():
    """Créer des clients"""
    print("\n👤 Création des clients...")
    customers_data = []

    for i in range(5):
        customer = {
            "email": fake.email(),
            "password": "password123",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": fake.phone_number(),
        }
        customers_data.append(customer)

        try:
            response = requests.post(
                f"{SERVICES['customers']}/api/v1/auth/register", json=customer
            )
            if response.status_code == 201:
                created_customer = response.json()
                print(
                    f"✅ Client créé: {customer['first_name']} {customer['last_name']} ({customer['email']})"
                )

                # Ajouter une adresse
                address = {
                    "street": fake.street_address(),
                    "city": fake.city(),
                    "postal_code": fake.postcode(),
                    "country": "France",
                    "is_default": True,
                }

                # Récupérer le token pour créer l'adresse
                login_response = requests.post(
                    f"{SERVICES['customers']}/api/v1/auth/login",
                    json={"email": customer["email"], "password": customer["password"]},
                )

                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}

                    addr_response = requests.post(
                        f"{SERVICES['customers']}/api/v1/addresses",
                        json=address,
                        headers=headers,
                    )
                    if addr_response.status_code == 201:
                        print(f"  📍 Adresse ajoutée: {address['city']}")

            else:
                print(f"❌ Erreur création client: {response.text}")
        except Exception as e:
            print(f"❌ Erreur: {e}")

    return customers_data


def test_cart_workflow(products, customers_data):
    """Tester le workflow panier -> commande"""
    print("\n🛒 Test du workflow panier -> commande...")

    if not customers_data or not products:
        print("❌ Pas de clients ou produits disponibles")
        return

    customer = customers_data[0]

    # Login du client
    try:
        login_response = requests.post(
            f"{SERVICES['customers']}/api/v1/auth/login",
            json={"email": customer["email"], "password": customer["password"]},
        )

        if login_response.status_code != 200:
            print(f"❌ Erreur login: {login_response.text}")
            return

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Créer un panier
        cart_response = requests.post(
            f"{SERVICES['cart']}/api/v1/carts",
            json={"customer_id": login_response.json()["customer"]["id"]},
        )

        if cart_response.status_code != 201:
            print(f"❌ Erreur création panier: {cart_response.text}")
            return

        cart = cart_response.json()
        print(f"✅ Panier créé (ID: {cart['id']})")

        # Ajouter des produits au panier
        selected_products = random.sample(products, min(3, len(products)))

        for product in selected_products:
            quantity = random.randint(1, 3)
            item_data = {"product_id": product["id"], "quantity": quantity}

            item_response = requests.post(
                f"{SERVICES['cart']}/api/v1/carts/{cart['id']}/items", json=item_data
            )

            if item_response.status_code == 201:
                print(f"✅ Produit ajouté au panier: {product['name']} x{quantity}")
            else:
                print(f"❌ Erreur ajout produit: {item_response.text}")

        # Récupérer le panier mis à jour
        cart_get_response = requests.get(
            f"{SERVICES['cart']}/api/v1/carts/{cart['id']}"
        )
        if cart_get_response.status_code == 200:
            updated_cart = cart_get_response.json()
            print(f"💰 Total panier: {updated_cart['total_amount']}€")

        # Passer commande
        print("\n📦 Passage de commande...")
        order_data = {
            "cart_id": cart["id"],
            "shipping_address": {
                "street": "123 Test Street",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France",
            },
            "billing_address": {
                "street": "123 Test Street",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France",
            },
        }

        order_response = requests.post(
            f"{SERVICES['orders']}/api/v1/orders", json=order_data, headers=headers
        )

        if order_response.status_code == 201:
            order = order_response.json()
            print(
                f"✅ Commande créée (ID: {order['id']}) - Total: {order['total_amount']}€"
            )

            # Vérifier l'impact sur le stock
            print("\n📊 Vérification impact sur le stock...")
            for item in updated_cart.get("items", []):
                product_id = item["product_id"]
                quantity_ordered = item["quantity"]

                # Vérifier le stock après commande
                stock_response = requests.get(f"{SERVICES['stock']}/api/v1/stock")
                if stock_response.status_code == 200:
                    stocks = stock_response.json()
                    for stock in stocks:
                        if stock["product_id"] == product_id:
                            print(
                                f"📦 Stock {product_id}: {stock['quantity']} disponible, {stock.get('reserved_quantity', 0)} réservé"
                            )

        else:
            print(f"❌ Erreur création commande: {order_response.text}")

    except Exception as e:
        print(f"❌ Erreur workflow: {e}")


def check_data_coordination():
    """Vérifier la coordination des données entre services"""
    print("\n🔍 Vérification de la coordination des données...")

    try:
        # Vérifier les produits
        products_response = requests.get(f"{SERVICES['products']}/api/v1/products")
        if products_response.status_code == 200:
            products = products_response.json()
            print(f"📦 {len(products)} produits dans Products API")

        # Vérifier le stock
        stock_response = requests.get(f"{SERVICES['stock']}/api/v1/stock")
        if stock_response.status_code == 200:
            stocks = stock_response.json()
            print(f"📊 {len(stocks)} entrées de stock dans Stock API")

        # Vérifier les clients
        try:
            customers_response = requests.get(
                f"{SERVICES['customers']}/api/v1/customers"
            )
            if customers_response.status_code == 200:
                customers = customers_response.json()
                print(f"👤 {len(customers)} clients dans Customers API")
        except:
            print("👤 Customers API nécessite une authentification")

        # Vérifier les magasins
        stores_response = requests.get(f"{SERVICES['stores']}/api/v1/stores")
        if stores_response.status_code == 200:
            stores = stores_response.json()
            print(f"🏪 {len(stores)} magasins dans Stores API")

        print("\n✅ Coordination des données vérifiée!")

    except Exception as e:
        print(f"❌ Erreur vérification: {e}")


def main():
    """Fonction principale"""
    print("🚀 Génération de données de test pour les microservices")
    print("=" * 60)

    if not wait_for_services():
        print("❌ Certains services ne sont pas prêts")
        return

    # Génération des données
    categories = create_categories()
    products = create_products(categories)
    stores = create_stores()
    create_stock_entries(products, stores)
    customers_data = create_customers()

    # Test des workflows
    test_cart_workflow(products, customers_data)

    # Vérification finale
    check_data_coordination()

    print("\n🎉 Génération de données terminée!")
    print("=" * 60)


if __name__ == "__main__":
    main()
