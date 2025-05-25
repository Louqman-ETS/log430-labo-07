from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple

from src.models import Produit, Categorie, Vente, LigneVente, Caisse

class ProduitDAO:
    """Classe pour gérer l'accès aux données des produits"""
    
    @staticmethod
    def get_by_id(db: Session, produit_id: int) -> Optional[Produit]:
        return db.query(Produit).filter(Produit.id == produit_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Produit]:
        return db.query(Produit).filter(Produit.code == code).first()
    
    @staticmethod
    def search_by_name(db: Session, name: str) -> List[Produit]:
        return db.query(Produit).filter(Produit.nom.ilike(f"%{name}%")).all()
    
    @staticmethod
    def search_by_category(db: Session, category_id: int) -> List[Produit]:
        return db.query(Produit).filter(Produit.categorie_id == category_id).all()
    
    @staticmethod
    def search(db: Session, term: str) -> List[Produit]:
        try:
            id_term = int(term)
        except ValueError:
            id_term = None
        
        query = db.query(Produit).filter(
            or_(
                Produit.nom.ilike(f"%{term}%"),
                Produit.code.ilike(f"%{term}%"),
                Produit.id == id_term if id_term is not None else False
            )
        )
        return query.all()
    
    @staticmethod
    def update_stock(db: Session, produit_id: int, quantity: int) -> bool:
        produit = db.query(Produit).filter(Produit.id == produit_id).with_for_update().first()
        if not produit:
            return False
        
        new_quantity = produit.quantite_stock + quantity
        if new_quantity < 0:
            return False
        
        produit.quantite_stock = new_quantity
        db.commit()
        return True


class CategorieDAO:
    """Classe pour gérer l'accès aux données des catégories"""
    
    @staticmethod
    def get_all(db: Session) -> List[Categorie]:
        return db.query(Categorie).all()
    
    @staticmethod
    def get_by_id(db: Session, categorie_id: int) -> Optional[Categorie]:
        return db.query(Categorie).filter(Categorie.id == categorie_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Categorie]:
        categorie = db.query(Categorie).filter(Categorie.nom == name).first()
        if categorie:
            return categorie
        
        return db.query(Categorie).filter(Categorie.nom.ilike(f"%{name}%")).first()


class VenteDAO:
    """Classe pour gérer l'accès aux données des ventes"""
    
    @staticmethod
    def create_vente(db: Session, caisse_id: int) -> Vente:
        vente = Vente(caisse_id=caisse_id)
        db.add(vente)
        db.commit()
        db.refresh(vente)
        return vente
    
    @staticmethod
    def add_product_to_vente(db: Session, vente_id: int, produit_id: int, quantite: int) -> Optional[LigneVente]:
        produit = db.query(Produit).filter(Produit.id == produit_id).with_for_update().first()
        if not produit or produit.quantite_stock < quantite:
            return None
        
        ligne = LigneVente(
            vente_id=vente_id,
            produit_id=produit_id,
            quantite=quantite,
            prix_unitaire=produit.prix
        )
        
        produit.quantite_stock -= quantite
        
        vente = db.query(Vente).filter(Vente.id == vente_id).with_for_update().first()
        vente.montant_total += produit.prix * quantite
        
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne
    
    @staticmethod
    def get_vente(db: Session, vente_id: int) -> Optional[Vente]:
        return db.query(Vente).filter(Vente.id == vente_id).first()
    
    @staticmethod
    def get_vente_with_lignes(db: Session, vente_id: int) -> Optional[Tuple[Vente, List[LigneVente]]]:
        vente = db.query(Vente).filter(Vente.id == vente_id).first()
        if not vente:
            return None
        
        lignes = db.query(LigneVente).filter(LigneVente.vente_id == vente_id).all()
        return vente, lignes
    
    @staticmethod
    def supprimer_vente(db: Session, vente_id: int) -> bool:
        result = VenteDAO.get_vente_with_lignes(db, vente_id)
        if not result:
            return False
        
        vente, lignes = result
        
        try:
            for ligne in lignes:
                produit = db.query(Produit).filter(Produit.id == ligne.produit_id).with_for_update().first()
                if produit:
                    produit.quantite_stock += ligne.quantite
            
            db.query(LigneVente).filter(LigneVente.vente_id == vente_id).delete()
            
            db.query(Vente).filter(Vente.id == vente_id).delete()
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


class CaisseDAO:
    """Classe pour gérer l'accès aux données des caisses"""
    
    @staticmethod
    def get_all(db: Session) -> List[Caisse]:
        return db.query(Caisse).all()
    
    @staticmethod
    def get_by_id(db: Session, caisse_id: int) -> Optional[Caisse]:
        return db.query(Caisse).filter(Caisse.id == caisse_id).first() 