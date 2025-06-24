# ADR 003: Adoption de Flask comme Framework Web

## Statut

Accepté

## Contexte

Le système de caisse multi-magasins nécessite une interface utilisateur accessible et intuitive. Les besoins principaux sont :
- Une interface web accessible depuis multiple postes de travail
- Une architecture permettant la gestion multi-utilisateurs
- Une solution facilement déployable et maintenable
- Une séparation claire entre l'interface utilisateur et la logique métier
- Un framework mature avec un écosystème riche

## Décision

Nous avons choisi d'adopter Flask comme framework web pour remplacer l'application console, pour les raisons suivantes :
- **Simplicité** : Framework minimaliste et facile à comprendre
- **Flexibilité** : Permet une architecture personnalisée selon nos besoins
- **Maturité** : Framework stable avec une large communauté
- **Écosystème** : Intégration native avec SQLAlchemy, Jinja2, et autres outils
- **Performance** : Léger et performant pour nos besoins
- **Documentation** : Excellente documentation et nombreux exemples

## Conséquences

### Avantages
- **Interface web** avec Bootstrap pour un design professionnel
- **Multi-utilisateurs** : Plusieurs caisses peuvent fonctionner simultanément
- **Accessibilité** : Interface accessible via navigateur web standard
- **Déploiement** : Application web déployable avec Docker
- **Maintenance** : Structure claire avec templates, routes et contrôleurs
- **Évolutivité** : Facilité d'ajout de nouvelles fonctionnalités
- **Intégration** : Compatible avec notre stack PostgreSQL + SQLAlchemy

### Inconvénients
- **Complexité** : Plus complexe qu'une application console simple
- **Dépendances supplémentaires** : Nécessite un serveur web
- **Sécurité** : Nécessité de gérer les aspects sécurité web
- **Ressources** : Consommation mémoire plus élevée qu'une application console

### Risques atténués
- **Courbe d'apprentissage** : Flask est réputé pour sa simplicité
- **Performance** : Flask est suffisamment performant pour notre usage
- **Maintenance** : Architecture MVC claire pour la maintenabilité

## Notes techniques
- **Version Flask** : 3.0+
- **Template Engine** : Jinja2 (intégré à Flask)
- **Frontend Framework** : Bootstrap 5 pour l'interface responsive
- **Serveur de développement** : Flask built-in server
- **Déploiement production** : Compatible avec Gunicorn, uWSGI
- **Port par défaut** : 8080
- **Configuration** : Variables d'environnement et fichier .env

## Migration effectuée
- Transformation complète de l'architecture console vers web
- Suppression des anciens fichiers : `main.py`, `run.py`, `service.py`, `dao.py`
- Création de la nouvelle structure Flask avec controllers, templates, static
- Mise à jour des tests pour la nouvelle architecture
- Documentation mise à jour (README, ADR, UML)