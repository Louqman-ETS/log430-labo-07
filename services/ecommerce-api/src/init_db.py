from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from typing import List

from src.database import engine, Base, SessionLocal
from src.models import Customer, CustomerAuth, Address, Cart, CartItem, Order, OrderItem
import src.schemas as schemas

logger = logging.getLogger(__name__)


def init_database():
    """Initialise la base de données avec des données de test"""
    logger.info("🚀 Initialisation de la base de données Ecommerce")

    # Créer les tables
    Base.metadata.create_all(bind=engine)

    # Créer une session
    db = SessionLocal()

    try:
        # Vérifier si des données existent déjà
        if db.query(Customer).count() > 0:
            logger.info("✅ Base de données déjà initialisée")
            return

        logger.info("📝 Création des données de test...")

        # Créer des clients de test
        customers = [
            Customer(
                email="john.doe@example.com",
                first_name="John",
                last_name="Doe",
                phone="+33123456789",
                date_of_birth=datetime(1990, 5, 15),
                is_active=True,
            ),
            Customer(
                email="jane.smith@example.com",
                first_name="Jane",
                last_name="Smith",
                phone="+33987654321",
                date_of_birth=datetime(1985, 8, 22),
                is_active=True,
            ),
            Customer(
                email="guest@example.com",
                first_name="Guest",
                last_name="User",
                phone=None,
                date_of_birth=None,
                is_active=True,
            ),
        ]

        for customer in customers:
            db.add(customer)
        db.commit()

        # Créer des authentifications pour les clients
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        auths = [
            CustomerAuth(
                customer_id=customers[0].id,
                password_hash=pwd_context.hash("password123"),
                last_login=datetime.utcnow(),
            ),
            CustomerAuth(
                customer_id=customers[1].id,
                password_hash=pwd_context.hash("password123"),
                last_login=datetime.utcnow(),
            ),
        ]

        for auth in auths:
            db.add(auth)
        db.commit()

        # Créer des adresses pour les clients
        addresses = [
            Address(
                customer_id=customers[0].id,
                type="shipping",
                title="Domicile",
                street_address="123 Rue de la Paix",
                city="Paris",
                postal_code="75001",
                country="France",
                is_default=True,
            ),
            Address(
                customer_id=customers[0].id,
                type="billing",
                title="Bureau",
                street_address="456 Avenue des Champs",
                city="Paris",
                postal_code="75008",
                country="France",
                is_default=True,
            ),
            Address(
                customer_id=customers[1].id,
                type="shipping",
                title="Domicile",
                street_address="789 Boulevard Saint-Germain",
                city="Paris",
                postal_code="75006",
                country="France",
                is_default=True,
            ),
        ]

        for address in addresses:
            db.add(address)
        db.commit()

        # Créer des paniers de test
        carts = [
            Cart(
                customer_id=customers[0].id,
                session_id=None,
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=30),
            ),
            Cart(
                customer_id=customers[1].id,
                session_id=None,
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=30),
            ),
            Cart(
                customer_id=None,
                session_id="guest-session-123",
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=30),
            ),
        ]

        for cart in carts:
            db.add(cart)
        db.commit()

        # Créer des éléments de panier
        cart_items = [
            CartItem(
                cart_id=carts[0].id,
                product_id=1,
                quantity=2,
                unit_price=Decimal("29.99"),
            ),
            CartItem(
                cart_id=carts[0].id,
                product_id=2,
                quantity=1,
                unit_price=Decimal("49.99"),
            ),
            CartItem(
                cart_id=carts[1].id,
                product_id=3,
                quantity=3,
                unit_price=Decimal("19.99"),
            ),
            CartItem(
                cart_id=carts[2].id,
                product_id=1,
                quantity=1,
                unit_price=Decimal("29.99"),
            ),
        ]

        for item in cart_items:
            db.add(item)
        db.commit()

        # Créer des commandes de test
        orders = [
            Order(
                order_number="ORD-1703123456",
                customer_id=customers[0].id,
                cart_id=None,
                status=models.OrderStatus.CONFIRMED,
                payment_status=models.PaymentStatus.PAID,
                subtotal=Decimal("109.97"),
                tax_amount=Decimal("21.99"),
                shipping_amount=Decimal("0.00"),
                total_amount=Decimal("131.96"),
                shipping_address="123 Rue de la Paix, 75001 Paris, France",
                billing_address="456 Avenue des Champs, 75008 Paris, France",
                confirmed_at=datetime.utcnow() - timedelta(days=2),
            ),
            Order(
                order_number="ORD-1703123457",
                customer_id=customers[1].id,
                cart_id=None,
                status=models.OrderStatus.SHIPPED,
                payment_status=models.PaymentStatus.PAID,
                subtotal=Decimal("59.97"),
                tax_amount=Decimal("11.99"),
                shipping_amount=Decimal("5.00"),
                total_amount=Decimal("76.96"),
                shipping_address="789 Boulevard Saint-Germain, 75006 Paris, France",
                billing_address="789 Boulevard Saint-Germain, 75006 Paris, France",
                confirmed_at=datetime.utcnow() - timedelta(days=1),
                shipped_at=datetime.utcnow() - timedelta(hours=12),
            ),
        ]

        for order in orders:
            db.add(order)
        db.commit()

        # Créer des éléments de commande
        order_items = [
            OrderItem(
                order_id=orders[0].id,
                product_id=1,
                product_name="Produit Test 1",
                quantity=2,
                unit_price=Decimal("29.99"),
            ),
            OrderItem(
                order_id=orders[0].id,
                product_id=2,
                product_name="Produit Test 2",
                quantity=1,
                unit_price=Decimal("49.99"),
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=3,
                product_name="Produit Test 3",
                quantity=3,
                unit_price=Decimal("19.99"),
            ),
        ]

        for item in order_items:
            db.add(item)
        db.commit()

        logger.info("✅ Base de données initialisée avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
