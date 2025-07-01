from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

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

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    cart_id = Column(Integer, nullable=True)  # Référence vers le panier original
    
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
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

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