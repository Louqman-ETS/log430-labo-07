from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

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
    categorie_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Relations
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, nom='{self.nom}', prix={self.prix})>" 