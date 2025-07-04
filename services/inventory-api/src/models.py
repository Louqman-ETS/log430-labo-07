from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relations
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, nom='{self.nom}')>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    quantite_stock = Column(Integer, default=0)
    seuil_alerte = Column(Integer, default=10)  # Seuil d'alerte pour le stock
    categorie_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    actif = Column(Boolean, default=True)  # Si le produit est actif

    # Relations
    category = relationship("Category", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, nom='{self.nom}', prix={self.prix}, stock={self.quantite_stock})>"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    type_mouvement = Column(String, nullable=False)  # "entree", "sortie", "ajustement"
    quantite = Column(Integer, nullable=False)
    raison = Column(
        String, nullable=True
    )  # "vente", "reapprovisionnement", "inventaire", etc.
    reference = Column(
        String, nullable=True
    )  # Référence externe (commande, facture, etc.)
    date_mouvement = Column(DateTime(timezone=True), server_default=func.now())
    utilisateur = Column(
        String, nullable=True
    )  # Utilisateur qui a effectué le mouvement

    # Relations
    product = relationship("Product", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement(id={self.id}, product_id={self.product_id}, type={self.type_mouvement}, quantite={self.quantite})>"


class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    type_alerte = Column(
        String, nullable=False
    )  # "stock_faible", "rupture", "surstock"
    message = Column(Text, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    resolu = Column(Boolean, default=False)
    date_resolution = Column(DateTime(timezone=True), nullable=True)

    # Relations
    product = relationship("Product")

    def __repr__(self):
        return f"<StockAlert(id={self.id}, product_id={self.product_id}, type={self.type_alerte}, resolu={self.resolu})>"
