from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from .. import db


class Magasin(db.Model):
    __tablename__ = "magasins"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True, nullable=False)
    adresse = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Relations
    caisses = relationship("Caisse", back_populates="magasin")
    stocks_magasin = relationship("StockMagasin", back_populates="magasin")

    def __repr__(self):
        return f"<Magasin(id={self.id}, nom='{self.nom}')>"


class Categorie(db.Model):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    produits = relationship("Produit", back_populates="categorie")

    def __repr__(self):
        return f"<Categorie(id={self.id}, nom='{self.nom}')>"


class Produit(db.Model):
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    nom = Column(String, index=True)
    description = Column(String, nullable=True)
    prix = Column(Float, nullable=False)
    quantite_stock = Column(Integer, default=0)  # Stock global/central
    categorie_id = Column(Integer, ForeignKey("categories.id"))

    categorie = relationship("Categorie", back_populates="produits")
    lignes_vente = relationship("LigneVente", back_populates="produit")
    stocks_magasin = relationship("StockMagasin", back_populates="produit")

    def __repr__(self):
        return f"<Produit(id={self.id}, nom='{self.nom}', prix={self.prix})>"


class Caisse(db.Model):
    __tablename__ = "caisses"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, index=True)  # Numéro dans le magasin (1-5)
    nom = Column(String, index=True)
    magasin_id = Column(Integer, ForeignKey("magasins.id"), nullable=False)

    # Relations
    magasin = relationship("Magasin", back_populates="caisses")
    ventes = relationship("Vente", back_populates="caisse")

    def __repr__(self):
        return f"<Caisse(id={self.id}, numero={self.numero}, nom='{self.nom}', magasin_id={self.magasin_id})>"


class StockMagasin(db.Model):
    __tablename__ = "stocks_magasin"

    id = db.Column(db.Integer, primary_key=True)
    magasin_id = db.Column(db.Integer, db.ForeignKey("magasins.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"), nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False, default=0)
    seuil_alerte = db.Column(db.Integer, nullable=False, default=20)

    # Relations
    magasin = db.relationship("Magasin", back_populates="stocks_magasin")
    produit = db.relationship("Produit", back_populates="stocks_magasin")

    def __repr__(self):
        return f"<StockMagasin(magasin_id={self.magasin_id}, produit_id={self.produit_id}, quantite={self.quantite_stock})>"


class Vente(db.Model):
    __tablename__ = "ventes"

    id = Column(Integer, primary_key=True, index=True)
    date_heure = Column(DateTime, default=datetime.datetime.utcnow)
    montant_total = Column(Float, default=0.0)
    caisse_id = Column(Integer, ForeignKey("caisses.id"))

    caisse = relationship("Caisse", back_populates="ventes")
    lignes = relationship("LigneVente", back_populates="vente")

    def __repr__(self):
        return f"<Vente(id={self.id}, montant_total={self.montant_total})>"


class LigneVente(db.Model):
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


class StockCentral(db.Model):
    __tablename__ = "stock_central"

    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"), nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False, default=0)
    seuil_alerte = db.Column(db.Integer, nullable=False, default=20)

    produit = db.relationship("Produit", backref="stock_central")


class DemandeReapprovisionnement(db.Model):
    __tablename__ = "demande_reappro"

    id = db.Column(db.Integer, primary_key=True)
    magasin_id = db.Column(db.Integer, db.ForeignKey("magasins.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"), nullable=False)
    quantite_demandee = db.Column(db.Integer, nullable=False)
    date_demande = db.Column(db.DateTime, nullable=False, default=db.func.now())
    statut = db.Column(
        db.String(20), nullable=False, default="en_attente"
    )  # en_attente, validee, livree

    magasin = db.relationship("Magasin", backref="demandes_reappro")
    produit = db.relationship("Produit", backref="demandes_reappro_produit")
