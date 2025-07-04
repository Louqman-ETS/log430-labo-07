from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from src.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True, nullable=False)
    adresse = Column(Text, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    actif = Column(Boolean, default=True)  # Si le magasin est actif
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    cash_registers = relationship(
        "CashRegister", back_populates="store", cascade="all, delete-orphan"
    )
    sales = relationship("Sale", back_populates="store")

    def __repr__(self):
        return f"<Store(id={self.id}, nom='{self.nom}')>"


class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(
        Integer, index=True, nullable=False
    )  # Number within the store (1-5)
    nom = Column(String, index=True, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    actif = Column(Boolean, default=True)  # Si la caisse est active
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    store = relationship("Store", back_populates="cash_registers")
    sales = relationship("Sale", back_populates="cash_register")

    def __repr__(self):
        return f"<CashRegister(id={self.id}, numero={self.numero}, nom='{self.nom}', store_id={self.store_id})>"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    cash_register_id = Column(Integer, ForeignKey("cash_registers.id"), nullable=False)
    date_vente = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    statut = Column(String, default="terminee")  # "en_cours", "terminee", "annulee"

    # Relations
    store = relationship("Store", back_populates="sales")
    cash_register = relationship("CashRegister", back_populates="sales")
    sale_lines = relationship(
        "SaleLine", back_populates="sale", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sale(id={self.id}, store_id={self.store_id}, total={self.total})>"


class SaleLine(Base):
    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Référence au Product (via API)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    sous_total = Column(Float, nullable=False)

    # Relation avec la vente
    sale = relationship("Sale", back_populates="sale_lines")

    def __repr__(self):
        return f"<SaleLine(id={self.id}, product_id={self.product_id}, quantite={self.quantite})>"


class StoreMetrics(Base):
    __tablename__ = "store_metrics"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    date_metrique = Column(DateTime, default=datetime.utcnow)
    total_ventes = Column(Float, default=0.0)
    nombre_transactions = Column(Integer, default=0)
    panier_moyen = Column(Float, default=0.0)

    # Relations
    store = relationship("Store")

    def __repr__(self):
        return f"<StoreMetrics(id={self.id}, store_id={self.store_id}, total_ventes={self.total_ventes})>"
