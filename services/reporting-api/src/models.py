from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from datetime import datetime
from .database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date_heure = Column(DateTime, default=datetime.utcnow, nullable=False)
    montant_total = Column(Float, default=0.0, nullable=False)
    store_id = Column(Integer, nullable=False)  # Reference to store via API
    cash_register_id = Column(Integer, nullable=False)  # Reference to cash register via API

    def __repr__(self):
        return f"<Sale(id={self.id}, montant_total={self.montant_total}, store_id={self.store_id})>"

class SaleLine(Base):
    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True, index=True)
    quantite = Column(Integer, default=1, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Reference to product via API

    def __repr__(self):
        return f"<SaleLine(id={self.id}, quantite={self.quantite}, product_id={self.product_id})>"

class StoreStock(Base):
    __tablename__ = "store_stocks"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)  # Reference to store via API
    product_id = Column(Integer, nullable=False)  # Reference to product via API
    quantite_stock = Column(Integer, nullable=False, default=0)
    seuil_alerte = Column(Integer, nullable=False, default=20)

    def __repr__(self):
        return f"<StoreStock(store_id={self.store_id}, product_id={self.product_id}, quantite={self.quantite_stock})>"

class CentralStock(Base):
    __tablename__ = "central_stocks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)  # Reference to product via API
    quantite_stock = Column(Integer, nullable=False, default=0)
    seuil_alerte = Column(Integer, nullable=False, default=20)

    def __repr__(self):
        return f"<CentralStock(product_id={self.product_id}, quantite={self.quantite_stock})>"

class RestockingRequest(Base):
    __tablename__ = "restocking_requests"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)  # Reference to store via API
    product_id = Column(Integer, nullable=False)  # Reference to product via API
    quantite_demandee = Column(Integer, nullable=False)
    date_demande = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(String(20), nullable=False, default="en_attente")  # en_attente, validee, livree

    def __repr__(self):
        return f"<RestockingRequest(store_id={self.store_id}, product_id={self.product_id}, quantite={self.quantite_demandee}, statut={self.statut})>" 