from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..models.models import Produit, Categorie, Magasin, StockMagasin
from .. import db

bp = Blueprint("produit", __name__, url_prefix="/produit")


@bp.route("/")
def liste():
    magasin_id = request.args.get("magasin_id")
    magasin = None

    if magasin_id:
        magasin = Magasin.query.get_or_404(magasin_id)
        # Récupérer les produits avec leur stock spécifique au magasin
        produits_avec_stock = (
            db.session.query(Produit, StockMagasin)
            .outerjoin(
                StockMagasin,
                (StockMagasin.produit_id == Produit.id)
                & (StockMagasin.magasin_id == magasin_id),
            )
            .all()
        )

        # Créer une liste de produits avec le stock du magasin
        produits = []
        for produit, stock_magasin in produits_avec_stock:
            # Ajouter temporairement le stock du magasin au produit
            produit.stock_magasin = stock_magasin.quantite_stock if stock_magasin else 0
            produits.append(produit)
    else:
        produits = Produit.query.all()
        # Pour la vue globale, on garde le stock global
        for produit in produits:
            produit.stock_magasin = produit.quantite_stock

    return render_template("produit/liste.html", produits=produits, magasin=magasin)


@bp.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    magasin_id = request.args.get("magasin_id") or request.form.get("magasin_id")
    magasin = None

    if magasin_id:
        magasin = Magasin.query.get_or_404(magasin_id)

    categories = Categorie.query.all()

    if request.method == "POST":
        produit = Produit(
            code=request.form["code"],
            nom=request.form["nom"],
            description=request.form["description"],
            prix=float(request.form["prix"]),
            quantite_stock=int(request.form["quantite_stock"]),
            categorie_id=int(request.form["categorie_id"]),
        )
        db.session.add(produit)
        try:
            db.session.commit()
            flash("Produit ajouté avec succès!", "success")
            if magasin:
                return redirect(url_for("produit.liste", magasin_id=magasin.id))
            else:
                return redirect(url_for("produit.liste"))
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de l'ajout du produit.", "danger")

    return render_template(
        "produit/ajouter.html", categories=categories, magasin=magasin
    )


@bp.route("/modifier/<int:id>", methods=["GET", "POST"])
def modifier(id):
    magasin_id = request.args.get("magasin_id") or request.form.get("magasin_id")
    magasin = None

    if magasin_id:
        magasin = Magasin.query.get_or_404(magasin_id)

    produit = Produit.query.get_or_404(id)
    categories = Categorie.query.all()

    if request.method == "POST":
        produit.code = request.form["code"]
        produit.nom = request.form["nom"]
        produit.description = request.form["description"]
        produit.prix = float(request.form["prix"])
        produit.quantite_stock = int(request.form["quantite_stock"])
        produit.categorie_id = int(request.form["categorie_id"])

        try:
            db.session.commit()
            flash("Produit modifié avec succès!", "success")
            if magasin:
                return redirect(url_for("produit.liste", magasin_id=magasin.id))
            else:
                return redirect(url_for("produit.liste"))
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de la modification du produit.", "danger")

    return render_template(
        "produit/modifier.html", produit=produit, categories=categories, magasin=magasin
    )
