from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)

    # Assurez-vous que les dossiers nécessaires existent
    os.makedirs(app.static_folder, exist_ok=True)
    os.makedirs(app.template_folder, exist_ok=True)

    # Enregistrer les blueprints
    from .controllers import caisse_controller
    from .controllers import produit_controller
    from .controllers import vente_controller
    from .controllers import home_controller
    from .controllers import rapport_controller
    from .controllers import stock_central_controller
    
    app.register_blueprint(home_controller.bp)
    app.register_blueprint(caisse_controller.bp)
    app.register_blueprint(produit_controller.bp)
    app.register_blueprint(vente_controller.bp)
    app.register_blueprint(rapport_controller.bp)
    app.register_blueprint(stock_central_controller.bp)

    # Route par défaut
    @app.route('/')
    def index():
        return render_template('home.html')

    return app 