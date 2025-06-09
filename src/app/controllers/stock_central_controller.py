from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy import func
from ..models.models import (
    StockCentral,
    DemandeReapprovisionnement,
    Produit,
    Caisse,
    Magasin,
)
from .. import db

bp = Blueprint("stock_central", __name__, url_prefix="/stock-central")


@bp.route("/")
def index():
    # Récupérer tous les produits avec leur stock central
    produits = (
        db.session.query(
            Produit, StockCentral.quantite_stock, StockCentral.seuil_alerte
        )
        .outerjoin(StockCentral)
        .all()
    )

    return render_template("stock_central/index.html", produits=produits)


@bp.route("/demandes")
def liste_demandes():
    # Récupérer toutes les demandes de réapprovisionnement
    demandes = DemandeReapprovisionnement.query.order_by(
        DemandeReapprovisionnement.date_demande.desc()
    ).all()

    return render_template("stock_central/demandes.html", demandes=demandes)


@bp.route("/demander-reappro", methods=["POST"])
def demander_reappro():
    try:
        data = request.json
        produit_id = data.get("produit_id")
        magasin_id = data.get("magasin_id")
        quantite = data.get("quantite")

        # Vérifier si le produit existe
        produit = Produit.query.get(produit_id)
        if not produit:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Produit avec l'ID {produit_id} introuvable",
                    }
                ),
                400,
            )

        # Si aucun magasin spécifié, prendre le premier disponible
        if not magasin_id:
            magasin = Magasin.query.first()
            if not magasin:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Aucun magasin disponible dans le système",
                        }
                    ),
                    400,
                )
            magasin_id = magasin.id
        else:
            # Vérifier si le magasin existe
            magasin = Magasin.query.get(magasin_id)
            if not magasin:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Magasin avec l'ID {magasin_id} introuvable",
                        }
                    ),
                    400,
                )

        # Créer la demande
        demande = DemandeReapprovisionnement(
            magasin_id=magasin_id, produit_id=produit_id, quantite_demandee=quantite
        )

        db.session.add(demande)
        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": f"Demande de réapprovisionnement créée pour {produit.nom}",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/valider-demande/<int:demande_id>", methods=["POST"])
def valider_demande(demande_id):
    try:
        from ..models.models import StockMagasin

        demande = DemandeReapprovisionnement.query.get_or_404(demande_id)
        stock_central = StockCentral.query.filter_by(
            produit_id=demande.produit_id
        ).first()

        if (
            not stock_central
            or stock_central.quantite_stock < demande.quantite_demandee
        ):
            return (
                jsonify({"status": "error", "message": "Stock central insuffisant"}),
                400,
            )

        # Mettre à jour le stock central
        stock_central.quantite_stock -= demande.quantite_demandee

        # Mettre à jour le stock du magasin
        stock_magasin = StockMagasin.query.filter_by(
            magasin_id=demande.magasin_id, produit_id=demande.produit_id
        ).first()

        if stock_magasin:
            stock_magasin.quantite_stock += demande.quantite_demandee
        else:
            # Créer un nouveau stock magasin si il n'existe pas
            nouveau_stock = StockMagasin(
                magasin_id=demande.magasin_id,
                produit_id=demande.produit_id,
                quantite_stock=demande.quantite_demandee,
                seuil_alerte=20,
            )
            db.session.add(nouveau_stock)

        # Mettre à jour le statut de la demande
        demande.statut = "validee"

        db.session.commit()

        return jsonify(
            {"status": "success", "message": "Demande validée et stocks mis à jour"}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
