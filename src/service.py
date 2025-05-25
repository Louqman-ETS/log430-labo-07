from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from contextlib import contextmanager

from src.dao import ProduitDAO, CategorieDAO, VenteDAO, CaisseDAO
from src.db import SessionLocal
from src.models import Produit, Categorie, Vente, LigneVente, Caisse


@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class ProduitService:
    """Service pour la gestion des produits"""

    @staticmethod
    def rechercher_produit(terme_recherche: str) -> List[Dict[str, Any]]:
        with get_db_session() as db:
            produits = ProduitDAO.search(db, terme_recherche)
            return [
                {
                    "id": p.id,
                    "code": p.code,
                    "nom": p.nom,
                    "prix": p.prix,
                    "stock": p.quantite_stock,
                    "categorie": p.categorie.nom if p.categorie else "Non catégorisé",
                }
                for p in produits
            ]

    @staticmethod
    def rechercher_par_categorie(terme_categorie: str) -> List[Dict[str, Any]]:
        with get_db_session() as db:
            categorie = CategorieDAO.get_by_name(db, terme_categorie)

            if not categorie:
                toutes_categories = CategorieDAO.get_all(db)

                for cat in toutes_categories:
                    if cat.nom.lower() == terme_categorie.lower():
                        categorie = cat
                        break

            if not categorie:
                return []

            produits = ProduitDAO.search_by_category(db, categorie.id)
            return [
                {
                    "id": p.id,
                    "code": p.code,
                    "nom": p.nom,
                    "prix": p.prix,
                    "stock": p.quantite_stock,
                    "categorie": p.categorie.nom,
                }
                for p in produits
            ]

    @staticmethod
    def get_produit_details(produit_id: int) -> Optional[Dict[str, Any]]:
        with get_db_session() as db:
            produit = ProduitDAO.get_by_id(db, produit_id)
            if not produit:
                return None

            return {
                "id": produit.id,
                "code": produit.code,
                "nom": produit.nom,
                "description": produit.description,
                "prix": produit.prix,
                "stock": produit.quantite_stock,
                "categorie": (
                    produit.categorie.nom if produit.categorie else "Non catégorisé"
                ),
            }


class CategorieService:
    """Service pour la gestion des catégories"""

    @staticmethod
    def liste_categories() -> List[Dict[str, Any]]:
        with get_db_session() as db:
            categories = CategorieDAO.get_all(db)
            return [
                {"id": c.id, "nom": c.nom, "description": c.description}
                for c in categories
            ]


class VenteService:
    """Service pour la gestion des ventes"""

    @staticmethod
    def demarrer_vente(caisse_id: int) -> Optional[int]:
        with get_db_session() as db:
            try:
                caisse = CaisseDAO.get_by_id(db, caisse_id)
                if not caisse:
                    return None

                vente = VenteDAO.create_vente(db, caisse_id)
                return vente.id
            except Exception:
                db.rollback()
                return None

    @staticmethod
    def ajouter_produit(
        vente_id: int, produit_id: int, quantite: int = 1
    ) -> Tuple[bool, str]:
        with get_db_session() as db:
            try:
                produit = ProduitDAO.get_by_id(db, produit_id)
                if not produit:
                    return False, "Produit introuvable"

                if produit.quantite_stock < quantite:
                    return (
                        False,
                        f"Stock insuffisant: {produit.quantite_stock} disponible(s)",
                    )

                ligne = VenteDAO.add_product_to_vente(
                    db, vente_id, produit_id, quantite
                )
                if not ligne:
                    return False, "Erreur lors de l'ajout du produit"

                return True, f"Produit '{produit.nom}' ajouté ({quantite})"
            except Exception as e:
                db.rollback()
                return False, f"Erreur: {str(e)}"

    @staticmethod
    def finaliser_vente(vente_id: int) -> Tuple[bool, Dict[str, Any]]:
        with get_db_session() as db:
            try:
                vente = VenteDAO.get_vente(db, vente_id)
                if not vente:
                    return False, {"erreur": "Vente introuvable"}

                lignes = []
                for ligne in vente.lignes:
                    produit = ProduitDAO.get_by_id(db, ligne.produit_id)
                    lignes.append(
                        {
                            "produit": produit.nom,
                            "quantite": ligne.quantite,
                            "prix_unitaire": ligne.prix_unitaire,
                            "sous_total": ligne.quantite * ligne.prix_unitaire,
                        }
                    )

                resultat = {
                    "vente_id": vente.id,
                    "date": vente.date_heure,
                    "caisse": vente.caisse.numero,
                    "total": vente.montant_total,
                    "lignes": lignes,
                }

                return True, resultat
            except Exception as e:
                return False, {"erreur": str(e)}

    @staticmethod
    def effectuer_retour(vente_id: int) -> Tuple[bool, str]:
        with get_db_session() as db:
            try:
                vente = VenteDAO.get_vente(db, vente_id)
                if not vente:
                    return False, f"Vente #{vente_id} introuvable"

                montant_total = vente.montant_total

                success = VenteDAO.supprimer_vente(db, vente_id)

                if success:
                    return (
                        True,
                        f"Retour effectué pour la vente #{vente_id} (montant: {montant_total:.2f} €). Produits remis en stock.",
                    )
                else:
                    return False, f"Erreur lors du retour de la vente #{vente_id}"
            except Exception as e:
                db.rollback()
                return False, f"Erreur: {str(e)}"
