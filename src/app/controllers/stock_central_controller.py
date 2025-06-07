from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy import func
from ..models.models import StockCentral, DemandeReapprovisionnement, Produit, Caisse
from .. import db

bp = Blueprint('stock_central', __name__, url_prefix='/stock-central')

@bp.route('/')
def index():
    # Récupérer tous les produits avec leur stock central
    produits = db.session.query(
        Produit,
        StockCentral.quantite_stock,
        StockCentral.seuil_alerte
    ).outerjoin(StockCentral).all()
    
    return render_template('stock_central/index.html', produits=produits)

@bp.route('/demandes')
def liste_demandes():
    # Récupérer toutes les demandes de réapprovisionnement
    demandes = DemandeReapprovisionnement.query.order_by(
        DemandeReapprovisionnement.date_demande.desc()
    ).all()
    
    return render_template('stock_central/demandes.html', demandes=demandes)

@bp.route('/demander-reappro', methods=['POST'])
def demander_reappro():
    try:
        data = request.json
        produit_id = data.get('produit_id')
        caisse_id = data.get('caisse_id')
        quantite = data.get('quantite')
        
        # Vérifier si le produit existe
        produit = Produit.query.get_or_404(produit_id)
        
        # Créer la demande
        demande = DemandeReapprovisionnement(
            caisse_id=caisse_id,
            produit_id=produit_id,
            quantite_demandee=quantite
        )
        
        db.session.add(demande)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Demande de réapprovisionnement créée pour {produit.nom}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/valider-demande/<int:demande_id>', methods=['POST'])
def valider_demande(demande_id):
    try:
        demande = DemandeReapprovisionnement.query.get_or_404(demande_id)
        stock_central = StockCentral.query.filter_by(produit_id=demande.produit_id).first()
        
        if not stock_central or stock_central.quantite_stock < demande.quantite_demandee:
            return jsonify({
                'status': 'error',
                'message': 'Stock central insuffisant'
            }), 400
            
        # Mettre à jour le stock central
        stock_central.quantite_stock -= demande.quantite_demandee
        
        # Mettre à jour le stock du magasin
        produit = demande.produit
        produit.quantite_stock += demande.quantite_demandee
        
        # Mettre à jour le statut de la demande
        demande.statut = 'validee'
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Demande validée et stocks mis à jour'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400 