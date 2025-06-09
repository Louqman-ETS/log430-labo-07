from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..models.models import Magasin, Caisse
from .. import db

bp = Blueprint("magasin", __name__, url_prefix="/magasin")


@bp.route("/")
def index():
    """Liste tous les magasins"""
    magasins = Magasin.query.all()
    return render_template("magasin/index.html", magasins=magasins)


@bp.route("/<int:magasin_id>")
def detail(magasin_id):
    """Redirige vers les caisses du magasin (plus de page détail)"""
    return redirect(url_for("magasin.caisses", magasin_id=magasin_id))


@bp.route("/<int:magasin_id>/caisses")
def caisses(magasin_id):
    """Liste les caisses du magasin"""
    magasin = Magasin.query.get_or_404(magasin_id)
    caisses = Caisse.query.filter_by(magasin_id=magasin_id).all()
    return render_template("caisse/index.html", caisses=caisses, magasin=magasin)
