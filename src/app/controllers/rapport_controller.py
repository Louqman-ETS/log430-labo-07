from flask import Blueprint, render_template
from sqlalchemy import func, desc
from ..models.models import Vente, LigneVente, Produit, Caisse
from .. import db

bp = Blueprint('rapport', __name__, url_prefix='/rapport')

@bp.route('/')
def index():
    # Statistiques globales
    total_ventes = db.session.query(func.sum(Vente.montant_total)).scalar() or 0
    nombre_ventes = db.session.query(Vente).count()
    
    # Ventes par magasin (caisse)
    ventes_par_caisse = db.session.query(
        Caisse.numero,
        Caisse.nom,
        func.count(Vente.id).label('nombre_ventes'),
        func.sum(Vente.montant_total).label('total_ventes')
    ).outerjoin(Vente).group_by(Caisse.id).all()
    
    # Produits les plus vendus
    produits_populaires = db.session.query(
        Produit.code,
        Produit.nom,
        func.sum(LigneVente.quantite).label('quantite_vendue'),
        func.sum(LigneVente.quantite * LigneVente.prix_unitaire).label('chiffre_affaires')
    ).join(LigneVente).group_by(Produit.id).order_by(desc('quantite_vendue')).limit(10).all()
    
    # État des stocks
    stocks = db.session.query(
        Produit.code,
        Produit.nom,
        Produit.quantite_stock,
        func.sum(LigneVente.quantite).label('quantite_vendue')
    ).outerjoin(LigneVente).group_by(Produit.id).order_by(Produit.quantite_stock).all()
    
    return render_template('rapport/index.html',
                         total_ventes=total_ventes,
                         nombre_ventes=nombre_ventes,
                         ventes_par_caisse=ventes_par_caisse,
                         produits_populaires=produits_populaires,
                         stocks=stocks) 