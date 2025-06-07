from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import or_
from ..models.models import Produit, Vente, LigneVente, Caisse
from .. import db

bp = Blueprint('vente', __name__, url_prefix='/vente')

@bp.route('/<int:caisse_id>')
def index(caisse_id):
    # Récupérer la caisse
    caisse = Caisse.query.get_or_404(caisse_id)
    
    # Récupérer tous les produits disponibles
    produits = Produit.query.filter(Produit.quantite_stock > 0).all()
    
    return render_template('vente/index.html', caisse=caisse, produits=produits)

@bp.route('/rechercher/<int:caisse_id>')
def rechercher_produits(caisse_id):
    terme = request.args.get('terme', '')
    if not terme:
        return jsonify([])
    
    # Rechercher les produits par code, nom ou description
    produits = Produit.query.filter(
        or_(
            Produit.code.ilike(f'%{terme}%'),
            Produit.nom.ilike(f'%{terme}%'),
            Produit.description.ilike(f'%{terme}%')
        ),
        Produit.quantite_stock > 0
    ).all()
    
    return jsonify([{
        'id': p.id,
        'code': p.code,
        'nom': p.nom,
        'prix': p.prix,
        'stock': p.quantite_stock
    } for p in produits])

@bp.route('/ajouter-produit/<int:caisse_id>', methods=['POST'])
def ajouter_produit(caisse_id):
    try:
        data = request.json
        produit_id = data.get('produit_id')
        quantite = int(data.get('quantite', 1))
        
        # Vérifier le produit et le stock
        produit = Produit.query.get_or_404(produit_id)
        if produit.quantite_stock < quantite:
            return jsonify({
                'status': 'error',
                'message': 'Stock insuffisant'
            }), 400
            
        return jsonify({
            'status': 'success',
            'produit': {
                'id': produit.id,
                'code': produit.code,
                'nom': produit.nom,
                'prix': produit.prix,
                'quantite': quantite,
                'total': produit.prix * quantite
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/finaliser/<int:caisse_id>', methods=['POST'])
def finaliser_vente(caisse_id):
    try:
        data = request.json
        produits = data.get('produits', [])
        
        if not produits:
            return jsonify({
                'status': 'error',
                'message': 'Aucun produit dans le panier'
            }), 400
        
        # Créer la vente
        vente = Vente(caisse_id=caisse_id, montant_total=0)
        db.session.add(vente)
        
        montant_total = 0
        for item in produits:
            produit = Produit.query.get(item['id'])
            quantite = int(item['quantite'])
            
            # Vérifier le stock une dernière fois
            if produit.quantite_stock < quantite:
                db.session.rollback()
                return jsonify({
                    'status': 'error',
                    'message': f'Stock insuffisant pour {produit.nom}'
                }), 400
            
            # Créer la ligne de vente
            ligne = LigneVente(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix
            )
            db.session.add(ligne)
            
            # Mettre à jour le stock
            produit.quantite_stock -= quantite
            montant_total += produit.prix * quantite
        
        # Mettre à jour le montant total
        vente.montant_total = montant_total
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Vente enregistrée avec succès',
            'vente_id': vente.id,
            'montant_total': montant_total
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400 