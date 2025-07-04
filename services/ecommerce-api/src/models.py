from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from src.database import Base

# ============================================================================
# ENUMS
# ============================================================================


class OrderStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(PyEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============================================================================
# CUSTOMER MODELS
# ============================================================================


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    auth = relationship("CustomerAuth", back_populates="customer", uselist=False)
    addresses = relationship("Address", back_populates="customer")
    carts = relationship("Cart", back_populates="customer")
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"


class CustomerAuth(Base):
    __tablename__ = "customer_auth"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=False, unique=True
    )
    password_hash = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    customer = relationship("Customer", back_populates="auth")

    def __repr__(self):
        return f"<CustomerAuth(customer_id={self.customer_id}, last_login={self.last_login})>"


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    type = Column(String, nullable=False)  # 'shipping', 'billing'
    title = Column(String, nullable=True)  # 'Domicile', 'Bureau', etc.
    street_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, default="France")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    customer = relationship("Customer", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id={self.id}, type='{self.type}', city='{self.city}')>"


# ============================================================================
# CART MODELS
# ============================================================================


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=True, index=True
    )  # Peut être null pour paniers invités
    session_id = Column(String, nullable=True, index=True)  # Pour les paniers invités
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relations
    customer = relationship("Customer", back_populates="carts")
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    @property
    def total_items(self):
        """Nombre total d'articles dans le panier"""
        return sum(item.quantity for item in self.items)

    @property
    def total_price(self):
        """Prix total du panier"""
        return sum(item.subtotal for item in self.items)

    def __repr__(self):
        return f"<Cart(id={self.id}, customer_id={self.customer_id}, items={len(self.items)})>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Référence vers Products API
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(
        Numeric(10, 2), nullable=False
    )  # Prix unitaire au moment de l'ajout
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    cart = relationship("Cart", back_populates="items")

    @property
    def subtotal(self):
        """Sous-total pour cet élément"""
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


# ============================================================================
# ORDER MODELS
# ============================================================================


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True
    )
    cart_id = Column(
        Integer, ForeignKey("carts.id"), nullable=True
    )  # Référence vers le panier original

    # Statut et état
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Montants
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    shipping_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Adresses (stockées comme JSON/Text pour simplifier)
    shipping_address = Column(String, nullable=False)
    billing_address = Column(String, nullable=False)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relations
    customer = relationship("Customer", back_populates="orders")
    cart = relationship("Cart")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status.value}')>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)  # Snapshot du nom
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    order = relationship("Order", back_populates="items")

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
