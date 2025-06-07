from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..models.models import Produit, Categorie
from .. import db

bp = Blueprint('produit', __name__, url_prefix='/produit')

@bp.route('/')
def liste():
    produits = Produit.query.all()
    return render_template('produit/liste.html', produits=produits)

@bp.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    categories = Categorie.query.all()
    if request.method == 'POST':
        produit = Produit(
            code=request.form['code'],
            nom=request.form['nom'],
            description=request.form['description'],
            prix=float(request.form['prix']),
            quantite_stock=int(request.form['quantite_stock']),
            categorie_id=int(request.form['categorie_id'])
        )
        db.session.add(produit)
        try:
            db.session.commit()
            flash('Produit ajouté avec succès!', 'success')
            return redirect(url_for('produit.liste'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'ajout du produit.', 'danger')
    
    return render_template('produit/ajouter.html', categories=categories)

@bp.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    produit = Produit.query.get_or_404(id)
    categories = Categorie.query.all()
    
    if request.method == 'POST':
        produit.code = request.form['code']
        produit.nom = request.form['nom']
        produit.description = request.form['description']
        produit.prix = float(request.form['prix'])
        produit.quantite_stock = int(request.form['quantite_stock'])
        produit.categorie_id = int(request.form['categorie_id'])
        
        try:
            db.session.commit()
            flash('Produit modifié avec succès!', 'success')
            return redirect(url_for('produit.liste'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la modification du produit.', 'danger')
    
    return render_template('produit/modifier.html', produit=produit, categories=categories) 