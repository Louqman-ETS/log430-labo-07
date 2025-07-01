from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=True, index=True)  # Peut être null pour paniers invités
    session_id = Column(String, nullable=True, index=True)  # Pour les paniers invités
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relations
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

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
    unit_price = Column(Numeric(10, 2), nullable=False)  # Prix unitaire au moment de l'ajout
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