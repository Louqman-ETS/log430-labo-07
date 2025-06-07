from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..models.models import Caisse, Vente, Produit
from .. import db
from sqlalchemy import or_

bp = Blueprint('caisse', __name__, url_prefix='/caisse')

@bp.route('/')
def index():
    caisses = Caisse.query.all()
    return render_template('caisse/index.html', caisses=caisses)

@bp.route('/<int:caisse_id>/options')
def options(caisse_id):
    caisse = Caisse.query.get_or_404(caisse_id)
    return render_template('caisse/options.html', caisse=caisse)

@bp.route('/<int:caisse_id>/recherche', methods=['GET', 'POST'])
def recherche_produits(caisse_id):
    caisse = Caisse.query.get_or_404(caisse_id)
    produits = []
    recherche = request.args.get('q', '')
    
    if recherche:
        produits = Produit.query.filter(
            or_(
                Produit.nom.ilike(f'%{recherche}%'),
                Produit.code.ilike(f'%{recherche}%'),
                Produit.description.ilike(f'%{recherche}%')
            )
        ).all()
    
    return render_template('caisse/recherche.html', caisse=caisse, produits=produits, recherche=recherche)

@bp.route('/<int:caisse_id>')
def detail(caisse_id):
    caisse = Caisse.query.get_or_404(caisse_id)
    return redirect(url_for('vente.index', caisse_id=caisse.id)) 