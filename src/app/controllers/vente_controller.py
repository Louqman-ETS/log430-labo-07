from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import or_, desc, join
from ..models.models import Produit, Vente, LigneVente, Caisse, StockMagasin
from .. import db

bp = Blueprint("vente", __name__, url_prefix="/vente")


@bp.route("/<int:caisse_id>")
def index(caisse_id):
    # Récupérer la caisse
    caisse = Caisse.query.get_or_404(caisse_id)

    # Récupérer tous les produits avec leur stock dans ce magasin
    produits_avec_stock = (
        db.session.query(Produit, StockMagasin)
        .join(StockMagasin)
        .filter(
            StockMagasin.magasin_id == caisse.magasin_id,
            StockMagasin.quantite_stock > 0,
        )
        .all()
    )

    # Créer une liste de produits avec le stock du magasin
    produits_disponibles = []
    for produit, stock in produits_avec_stock:
        # Ajouter temporairement le stock du magasin au produit
        produit.stock_magasin = stock.quantite_stock
        produits_disponibles.append(produit)

    return render_template(
        "vente/index.html", caisse=caisse, produits=produits_disponibles
    )


@bp.route("/retours/<int:caisse_id>")
def retours(caisse_id):
    # Récupérer la caisse
    caisse = Caisse.query.get_or_404(caisse_id)

    # Récupérer les ventes récentes de cette caisse (dernières 24h par exemple)
    from datetime import datetime, timedelta

    hier = datetime.now() - timedelta(days=1)

    ventes = (
        Vente.query.filter(Vente.caisse_id == caisse_id, Vente.date_heure >= hier)
        .order_by(desc(Vente.date_heure))
        .all()
    )

    return render_template("vente/retour.html", caisse=caisse, ventes=ventes)


@bp.route("/annuler/<int:vente_id>")
def annuler(vente_id):
    try:
        vente = Vente.query.get_or_404(vente_id)
        caisse_id = vente.caisse_id

        # Récupérer la caisse pour connaître le magasin
        caisse = Caisse.query.get_or_404(caisse_id)

        # Remettre les produits en stock dans le magasin
        for ligne in vente.lignes:
            stock_magasin = StockMagasin.query.filter_by(
                magasin_id=caisse.magasin_id, produit_id=ligne.produit_id
            ).first()

            if stock_magasin:
                stock_magasin.quantite_stock += ligne.quantite

        # Supprimer la vente et ses lignes
        db.session.delete(vente)
        db.session.commit()

        flash(
            f"Vente #{vente_id} annulée avec succès. Produits remis en stock.",
            "success",
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'annulation de la vente: {str(e)}", "error")

    return redirect(url_for("vente.retours", caisse_id=caisse_id))


@bp.route("/rechercher/<int:caisse_id>")
def rechercher_produits(caisse_id):
    terme = request.args.get("terme", "")
    if not terme:
        return jsonify([])

    # Récupérer la caisse pour connaître le magasin
    caisse = Caisse.query.get_or_404(caisse_id)

    # Rechercher les produits par code, nom ou description dans ce magasin
    query = (
        db.session.query(Produit, StockMagasin)
        .join(StockMagasin)
        .filter(
            or_(
                Produit.code.ilike(f"%{terme}%"),
                Produit.nom.ilike(f"%{terme}%"),
                Produit.description.ilike(f"%{terme}%"),
            ),
            StockMagasin.magasin_id == caisse.magasin_id,
            StockMagasin.quantite_stock > 0,
        )
        .all()
    )

    return jsonify(
        [
            {
                "id": p.id,
                "code": p.code,
                "nom": p.nom,
                "prix": p.prix,
                "stock": stock.quantite_stock,
            }
            for p, stock in query
        ]
    )


@bp.route("/ajouter-produit/<int:caisse_id>", methods=["POST"])
def ajouter_produit(caisse_id):
    try:
        data = request.json
        produit_id = data.get("produit_id")
        quantite = int(data.get("quantite", 1))

        # Récupérer la caisse pour connaître le magasin
        caisse = Caisse.query.get_or_404(caisse_id)

        # Vérifier le produit et le stock dans ce magasin
        produit = Produit.query.get_or_404(produit_id)
        stock_magasin = StockMagasin.query.filter_by(
            magasin_id=caisse.magasin_id, produit_id=produit_id
        ).first()

        if not stock_magasin or stock_magasin.quantite_stock < quantite:
            return jsonify({"status": "error", "message": "Stock insuffisant"}), 400

        return jsonify(
            {
                "status": "success",
                "produit": {
                    "id": produit.id,
                    "code": produit.code,
                    "nom": produit.nom,
                    "prix": produit.prix,
                    "quantite": quantite,
                    "total": produit.prix * quantite,
                },
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/finaliser/<int:caisse_id>", methods=["POST"])
def finaliser_vente(caisse_id):
    try:
        data = request.json
        produits = data.get("produits", [])

        if not produits:
            return (
                jsonify({"status": "error", "message": "Aucun produit dans le panier"}),
                400,
            )

        # Récupérer la caisse pour connaître le magasin
        caisse = Caisse.query.get_or_404(caisse_id)

        # Protection contre les doublons : vérifier s'il y a une vente identique récente
        from datetime import datetime, timedelta

        maintenant = datetime.now()
        il_y_a_5_secondes = maintenant - timedelta(seconds=5)

        # Calculer le montant total de la vente à créer
        montant_prevu = sum(float(p["quantite"]) * float(p["prix"]) for p in produits)

        # Chercher une vente identique récente
        vente_recente = Vente.query.filter(
            Vente.caisse_id == caisse_id,
            Vente.date_heure >= il_y_a_5_secondes,
            Vente.montant_total == montant_prevu,
        ).first()

        if vente_recente:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Cette vente semble être un doublon. Vente déjà enregistrée.",
                    }
                ),
                400,
            )

        # Créer la vente
        vente = Vente(caisse_id=caisse_id, montant_total=0)
        db.session.add(vente)

        montant_total = 0
        for item in produits:
            produit = Produit.query.get(item["id"])
            quantite = int(item["quantite"])

            # Vérifier le stock dans ce magasin une dernière fois
            stock_magasin = StockMagasin.query.filter_by(
                magasin_id=caisse.magasin_id, produit_id=produit.id
            ).first()

            if not stock_magasin or stock_magasin.quantite_stock < quantite:
                db.session.rollback()
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Stock insuffisant pour {produit.nom}",
                        }
                    ),
                    400,
                )

            # Créer la ligne de vente
            ligne = LigneVente(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix,
            )
            db.session.add(ligne)

            # Mettre à jour le stock du magasin (pas le stock global du produit)
            stock_magasin.quantite_stock -= quantite
            montant_total += produit.prix * quantite

        # Mettre à jour le montant total
        vente.montant_total = montant_total

        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": "Vente enregistrée avec succès",
                "vente_id": vente.id,
                "montant_total": montant_total,
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
