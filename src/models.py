from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
import datetime

from src.db import Base

# Définition des modèles


class Categorie(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    produits = relationship("Produit", back_populates="categorie")

    def __repr__(self):
        return f"<Categorie(id={self.id}, nom='{self.nom}')>"


class Produit(Base):
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    nom = Column(String, index=True)
    description = Column(String, nullable=True)
    prix = Column(Float, nullable=False)
    quantite_stock = Column(Integer, default=0)
    categorie_id = Column(Integer, ForeignKey("categories.id"))

    categorie = relationship("Categorie", back_populates="produits")
    lignes_vente = relationship("LigneVente", back_populates="produit")

    def __repr__(self):
        return f"<Produit(id={self.id}, nom='{self.nom}', prix={self.prix})>"


class Caisse(Base):
    __tablename__ = "caisses"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, index=True)
    nom = Column(String, index=True)

    ventes = relationship("Vente", back_populates="caisse")

    def __repr__(self):
        return f"<Caisse(id={self.id}, numero={self.numero}, nom='{self.nom}')>"


class Vente(Base):
    __tablename__ = "ventes"

    id = Column(Integer, primary_key=True, index=True)
    date_heure = Column(DateTime, default=datetime.datetime.utcnow)
    montant_total = Column(Float, default=0.0)
    caisse_id = Column(Integer, ForeignKey("caisses.id"))

    caisse = relationship("Caisse", back_populates="ventes")
    lignes = relationship("LigneVente", back_populates="vente")

    def __repr__(self):
        return f"<Vente(id={self.id}, montant_total={self.montant_total})>"


class LigneVente(Base):
    __tablename__ = "lignes_vente"

    id = Column(Integer, primary_key=True, index=True)
    quantite = Column(Integer, default=1)
    prix_unitaire = Column(Float)
    vente_id = Column(Integer, ForeignKey("ventes.id"))
    produit_id = Column(Integer, ForeignKey("produits.id"))

    vente = relationship("Vente", back_populates="lignes")
    produit = relationship("Produit", back_populates="lignes_vente")

    def __repr__(self):
        return f"<LigneVente(id={self.id}, quantite={self.quantite}, produit_id={self.produit_id})>"
