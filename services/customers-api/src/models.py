from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

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

    def __repr__(self):
        return f"<Customer(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

class CustomerAuth(Base):
    __tablename__ = "customer_auth"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, unique=True)
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