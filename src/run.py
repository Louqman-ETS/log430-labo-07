from app import create_app, db
from app.models.models import Caisse, Categorie

app = create_app()

# Créer les tables de la base de données
with app.app_context():
    db.create_all()
    
    if not Categorie.query.first():
        categorie_default = Categorie(nom="Général", description="Catégorie générale")
        db.session.add(categorie_default)
        db.session.commit()
    
    # Créer les caisses si elles n'existent pas
    if not Caisse.query.first():
        caisses = [
            Caisse(numero=1, nom="Caisse 1"),
            Caisse(numero=2, nom="Caisse 2"),
            Caisse(numero=3, nom="Caisse 3"),
            Caisse(numero=4, nom="Caisse 4"),
            Caisse(numero=5, nom="Caisse 5"),
        ]
        for caisse in caisses:
            db.session.add(caisse)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 