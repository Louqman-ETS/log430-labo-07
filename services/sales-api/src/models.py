from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)  # Référence au Store (via API)
    cash_register_id = Column(Integer, nullable=False)  # Référence à la CashRegister (via API)
    date_vente = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    
    # Relation avec les lignes de vente
    sale_lines = relationship("SaleLine", back_populates="sale", cascade="all, delete-orphan")

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