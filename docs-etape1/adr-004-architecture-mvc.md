# ADR 004: Adoption de l'Architecture MVC

## Statut

Accepté

## Contexte

Le passage à Flask nécessite une organisation structurée du code pour maintenir la maintenabilité et la clarté du projet. Les besoins principaux sont :
- Une séparation claire des responsabilités dans l'application web
- Une architecture évolutive pour faciliter l'ajout de nouvelles fonctionnalités
- Une structure familière aux développeurs web
- Une organisation du code qui facilite les tests et la maintenance
- Une approche qui respecte les bonnes pratiques du développement web

Les alternatives considérées étaient :
- **Architecture en couches** : Bien mais moins adaptée aux applications web
- **Architecture MVC** : Standard pour les applications web avec Flask

## Décision

Nous avons choisi d'adopter l'architecture MVC (Model-View-Controller) pour notre application Flask, avec l'organisation suivante :

### Model (Modèle)
- **Responsabilité** : Gestion des données et logique métier
- **Implémentation** : Modèles SQLAlchemy dans `src/app/models/`
- **Contenu** : Entités (Magasin, Caisse, Produit, Vente, Stock), relations, validations

### View (Vue)
- **Responsabilité** : Présentation et interface utilisateur
- **Implémentation** : Templates Jinja2 dans `src/app/templates/`
- **Contenu** : Templates HTML, CSS, JavaScript, composants Bootstrap

### Controller (Contrôleur)
- **Responsabilité** : Logique de traitement et coordination
- **Implémentation** : Blueprints Flask dans `src/app/controllers/`
- **Contenu** : Routes, validation des données, orchestration des modèles

## Implémentation

### Structure des Controllers
```
src/app/controllers/
├── home_controller.py          # Dashboard principal
├── magasin_controller.py       # Gestion des magasins
├── caisse_controller.py        # Gestion des caisses
├── produit_controller.py       # Gestion des produits
├── vente_controller.py         # Point de vente et retours
├── rapport_controller.py       # Rapports stratégiques
└── stock_central_controller.py # Gestion centralisée des stocks
```

### Structure des Templates
```
src/app/templates/
├── base.html                   # Template de base
├── home.html                   # Dashboard principal
├── magasin/                    # Templates magasins
├── caisse/                     # Templates caisses
├── produit/                    # Templates produits
├── vente/                      # Templates point de vente
├── rapport/                    # Templates rapports
└── stock_central/              # Templates gestion stocks
```

### Structure des Models
```
src/app/models/
└── models.py                   # Tous les modèles SQLAlchemy
    ├── Magasin                 # Modèle magasin
    ├── Caisse                  # Modèle caisse
    ├── Produit                 # Modèle produit
    ├── Vente                   # Modèle vente
    ├── LigneVente              # Modèle ligne de vente
    └── Stock                   # Modèle stock
```

## Conséquences

### Avantages
- **Séparation des responsabilités** : Chaque composant a un rôle bien défini
- **Maintenabilité** : Code organisé et facile à modifier
- **Réutilisabilité** : Templates et modèles réutilisables
- **Testabilité** : Chaque couche peut être testée indépendamment
- **Évolutivité** : Facilité d'ajout de nouvelles fonctionnalités
- **Collaboration** : Plusieurs développeurs peuvent travailler en parallèle
- **Standard** : Architecture familière aux développeurs web

### Inconvénients
- **Complexité initiale** : Plus de fichiers et de structure à gérer
- **Courbe d'apprentissage** : Nécessite de comprendre l'organisation MVC

### Risques atténués
- **Complexité maîtrisée** : Structure claire avec des responsabilités bien définies
- **Documentation** : ADR et README expliquent l'organisation
- **Conventions** : Respect des conventions Flask pour la structure

## Bénéfices observés

### Pour le développement
- **Navigation intuitive** : Structure logique des fichiers
- **Isolation des changements** : Modification d'une vue n'affecte pas le modèle
- **Réutilisation** : Templates de base réutilisés partout
- **Debug facilité** : Erreurs localisées dans la bonne couche

### Pour la maintenance
- **Modularité** : Chaque module peut être modifié indépendamment
- **Extensibilité** : Ajout facile de nouveaux contrôleurs/vues
- **Tests ciblés** : Tests spécifiques par couche

## Notes techniques
- **Blueprints Flask** : Un par contrôleur pour l'organisation modulaire
- **URL routing** : Organisation logique des URLs par module
- **Error handling** : Gestion d'erreurs cohérente dans chaque couche

## Standards adoptés
- **Nommage** : Convention `module_controller.py` pour les contrôleurs
- **URLs** : Structure `/module/action` (ex: `/produit/ajouter`)
- **Templates** : Organisation en dossiers par module
- **Models** : Un seul fichier `models.py` avec toutes les entités
- **Imports** : Imports relatifs pour la cohérence 