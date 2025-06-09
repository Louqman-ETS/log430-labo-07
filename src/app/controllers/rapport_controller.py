from flask import Blueprint, render_template, request
from sqlalchemy import func, desc, case
from ..models.models import Vente, LigneVente, Produit, Caisse, Magasin, StockMagasin
from .. import db
from datetime import datetime, timedelta

bp = Blueprint("rapport", __name__, url_prefix="/rapport")


@bp.route("/")
def index():
    """Rapport consolidé stratégique pour la maison mère ou par magasin"""

    # Récupérer le magasin sélectionné s'il y en a un
    magasin_id = request.args.get("magasin_id", type=int)
    magasin_selectionne = None

    if magasin_id:
        magasin_selectionne = Magasin.query.get_or_404(magasin_id)

    # === PÉRIODE D'ANALYSE ===
    aujourd_hui = datetime.now()
    debut_mois = aujourd_hui.replace(day=1)
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    # === FILTRE BASE POUR MAGASIN ===
    def appliquer_filtre_magasin(query_ventes):
        """Applique le filtre magasin si sélectionné"""
        if magasin_id:
            return query_ventes.join(Caisse).filter(Caisse.magasin_id == magasin_id)
        return query_ventes

    # === 1. PERFORMANCES GLOBALES ===
    # Chiffre d'affaires total
    query_ca_total = db.session.query(func.sum(Vente.montant_total))
    ca_total = appliquer_filtre_magasin(query_ca_total).scalar() or 0

    query_ca_mois = db.session.query(func.sum(Vente.montant_total)).filter(
        Vente.date_heure >= debut_mois
    )
    ca_mois = appliquer_filtre_magasin(query_ca_mois).scalar() or 0

    query_ca_semaine = db.session.query(func.sum(Vente.montant_total)).filter(
        Vente.date_heure >= debut_semaine
    )
    ca_semaine = appliquer_filtre_magasin(query_ca_semaine).scalar() or 0

    # Nombre de transactions
    query_nb_total = db.session.query(Vente)
    nb_ventes_total = appliquer_filtre_magasin(query_nb_total).count()

    query_nb_mois = db.session.query(Vente).filter(Vente.date_heure >= debut_mois)
    nb_ventes_mois = appliquer_filtre_magasin(query_nb_mois).count()

    # Ticket moyen
    ticket_moyen = ca_total / nb_ventes_total if nb_ventes_total > 0 else 0

    # === 2. PERFORMANCES PAR MAGASIN ===
    if magasin_id:
        # Pour un magasin spécifique, on affiche les performances par caisse
        ventes_par_caisse = (
            db.session.query(
                Caisse.nom.label("nom_caisse"),
                Caisse.numero,
                func.count(Vente.id).label("nombre_ventes"),
                func.sum(Vente.montant_total).label("chiffre_affaires"),
                func.avg(Vente.montant_total).label("ticket_moyen"),
            )
            .select_from(Caisse)
            .outerjoin(Vente, Caisse.id == Vente.caisse_id)
            .filter(Caisse.magasin_id == magasin_id)
            .group_by(Caisse.id, Caisse.nom, Caisse.numero)
            .order_by(desc("chiffre_affaires"))
            .all()
        )
    else:
        # Vue globale par magasin
        ventes_par_caisse = (
            db.session.query(
                Magasin.nom.label("nom_caisse"),
                Magasin.adresse.label("numero"),
                func.count(Vente.id).label("nombre_ventes"),
                func.sum(Vente.montant_total).label("chiffre_affaires"),
                func.avg(Vente.montant_total).label("ticket_moyen"),
            )
            .select_from(Magasin)
            .outerjoin(Caisse, Magasin.id == Caisse.magasin_id)
            .outerjoin(Vente, Caisse.id == Vente.caisse_id)
            .group_by(Magasin.id, Magasin.nom, Magasin.adresse)
            .order_by(desc("chiffre_affaires"))
            .all()
        )

    # === 3. TOP PRODUITS (GLOBAL OU PAR MAGASIN) ===
    query_top_produits = (
        db.session.query(
            Produit.code,
            Produit.nom,
            Produit.prix,
            func.sum(LigneVente.quantite).label("quantite_totale"),
            func.sum(LigneVente.quantite * LigneVente.prix_unitaire).label(
                "ca_produit"
            ),
            func.count(func.distinct(Vente.id)).label("nb_commandes"),
        )
        .select_from(Produit)
        .join(LigneVente, Produit.id == LigneVente.produit_id)
        .join(Vente, LigneVente.vente_id == Vente.id)
    )

    if magasin_id:
        query_top_produits = query_top_produits.join(
            Caisse, Vente.caisse_id == Caisse.id
        ).filter(Caisse.magasin_id == magasin_id)

    top_produits = (
        query_top_produits.group_by(Produit.id, Produit.code, Produit.nom, Produit.prix)
        .order_by(desc("quantite_totale"))
        .limit(15)
        .all()
    )

    # === 4. ANALYSE DES STOCKS CRITIQUES ===
    if magasin_id:
        # Pour un magasin spécifique, utiliser les stocks du magasin
        stocks_critique = (
            db.session.query(
                Produit.code,
                Produit.nom,
                Produit.prix,
                StockMagasin.quantite_stock,
                func.sum(LigneVente.quantite).label("ventes_totales"),
                case(
                    (StockMagasin.quantite_stock == 0, "RUPTURE"),
                    (StockMagasin.quantite_stock <= 5, "CRITIQUE"),
                    (StockMagasin.quantite_stock <= 20, "FAIBLE"),
                    else_="NORMAL",
                ).label("statut_stock"),
            )
            .select_from(Produit)
            .join(StockMagasin, Produit.id == StockMagasin.produit_id)
            .outerjoin(LigneVente, Produit.id == LigneVente.produit_id)
            .outerjoin(Vente, LigneVente.vente_id == Vente.id)
            .outerjoin(Caisse, Vente.caisse_id == Caisse.id)
            .filter(StockMagasin.magasin_id == magasin_id)
            .group_by(
                Produit.id,
                Produit.code,
                Produit.nom,
                Produit.prix,
                StockMagasin.quantite_stock,
            )
            .order_by(StockMagasin.quantite_stock)
            .all()
        )
    else:
        # Vue globale : somme des stocks de tous les magasins
        stocks_critique = (
            db.session.query(
                Produit.code,
                Produit.nom,
                Produit.prix,
                func.sum(StockMagasin.quantite_stock).label("quantite_stock"),
                func.sum(LigneVente.quantite).label("ventes_totales"),
                case(
                    (func.sum(StockMagasin.quantite_stock) == 0, "RUPTURE"),
                    (func.sum(StockMagasin.quantite_stock) <= 5, "CRITIQUE"),
                    (func.sum(StockMagasin.quantite_stock) <= 20, "FAIBLE"),
                    else_="NORMAL",
                ).label("statut_stock"),
            )
            .select_from(Produit)
            .join(StockMagasin, Produit.id == StockMagasin.produit_id)
            .outerjoin(LigneVente, Produit.id == LigneVente.produit_id)
            .group_by(Produit.id, Produit.code, Produit.nom, Produit.prix)
            .order_by(func.sum(StockMagasin.quantite_stock))
            .all()
        )

    # Compter les alertes
    stocks_rupture = len([s for s in stocks_critique if s.quantite_stock == 0])
    stocks_faibles = len([s for s in stocks_critique if 0 < s.quantite_stock <= 20])

    # === 5. TENDANCES TEMPORELLES ===
    # Ventes des 7 derniers jours
    ventes_quotidiennes = []
    for i in range(7):
        jour = aujourd_hui - timedelta(days=i)
        debut_jour = jour.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_jour = debut_jour + timedelta(days=1)

        query_ca_jour = db.session.query(func.sum(Vente.montant_total)).filter(
            Vente.date_heure >= debut_jour, Vente.date_heure < fin_jour
        )
        ca_jour = appliquer_filtre_magasin(query_ca_jour).scalar() or 0

        query_nb_jour = db.session.query(Vente).filter(
            Vente.date_heure >= debut_jour, Vente.date_heure < fin_jour
        )
        nb_ventes_jour = appliquer_filtre_magasin(query_nb_jour).count()

        ventes_quotidiennes.append(
            {
                "date": jour.strftime("%d/%m"),
                "jour": jour.strftime("%A"),
                "ca": ca_jour,
                "nb_ventes": nb_ventes_jour,
            }
        )

    ventes_quotidiennes.reverse()  # Ordre chronologique

    # === 6. PRODUITS À RÉAPPROVISIONNER ===
    produits_reappro = []
    for stock in stocks_critique:
        if stock.ventes_totales and stock.ventes_totales > 0:
            ventes_par_jour = stock.ventes_totales / 30
            jours_restants = (
                stock.quantite_stock / ventes_par_jour if ventes_par_jour > 0 else 999
            )

            if jours_restants <= 14:
                produits_reappro.append(
                    {
                        "code": stock.code,
                        "nom": stock.nom,
                        "stock_actuel": stock.quantite_stock,
                        "ventes_mensuelles": stock.ventes_totales or 0,
                        "jours_restants": int(jours_restants),
                        "priorite": "URGENT" if jours_restants <= 7 else "MOYEN",
                    }
                )

    produits_reappro.sort(key=lambda x: x["jours_restants"])

    # === LISTE DES MAGASINS POUR LE SÉLECTEUR ===
    tous_magasins = Magasin.query.order_by(Magasin.nom).all()

    return render_template(
        "rapport/index.html",
        # Contexte magasin
        magasin_selectionne=magasin_selectionne,
        tous_magasins=tous_magasins,
        # Performances globales
        ca_total=ca_total,
        ca_mois=ca_mois,
        ca_semaine=ca_semaine,
        nb_ventes_total=nb_ventes_total,
        nb_ventes_mois=nb_ventes_mois,
        ticket_moyen=ticket_moyen,
        # Par magasin/caisse
        ventes_par_caisse=ventes_par_caisse,
        # Produits
        top_produits=top_produits,
        # Stocks
        stocks_critique=stocks_critique,
        stocks_rupture=stocks_rupture,
        stocks_faibles=stocks_faibles,
        produits_reappro=produits_reappro,
        # Tendances
        ventes_quotidiennes=ventes_quotidiennes,
        # Contexte temporel
        date_rapport=aujourd_hui.strftime("%d/%m/%Y à %H:%M"),
    )
