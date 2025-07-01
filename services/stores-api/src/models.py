from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True, nullable=False)
    adresse = Column(Text, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Relations
    cash_registers = relationship("CashRegister", back_populates="store")

    def __repr__(self):
        return f"<Store(id={self.id}, nom='{self.nom}')>"

class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, index=True, nullable=False)  # Number within the store (1-5)
    nom = Column(String, index=True, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)

    # Relations
    store = relationship("Store", back_populates="cash_registers")

    def __repr__(self):
        return f"<CashRegister(id={self.id}, numero={self.numero}, nom='{self.nom}', store_id={self.store_id})>" 