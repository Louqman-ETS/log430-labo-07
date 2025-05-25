import os
import sys
from typing import Dict, Any, List, Optional

from src.service import ProduitService, CategorieService, VenteService
from src.create_db import initialize_db, initialize_data

class CaisseMagasinApp:
    """Application console pour le système de caisse de magasin"""
    
    def __init__(self):
        self.vente_en_cours: Optional[int] = None
        self.caisse_id: Optional[int] = None

        # S'assurer que la base de données est initialisée
        initialize_db()
        initialize_data()
    
    def afficher_menu_principal(self):
        """Affiche le menu principal de l'application"""
        print("\n" + "=" * 40)
        print("    SYSTÈME DE CAISSE - MAGASIN LOG430")
        print("=" * 40)
        
        options = []
        
        if self.caisse_id is None:
            options.append("Sélectionner une caisse")
        else:
            print(f"\nCaisse active: {self.caisse_id}")
            
            if self.vente_en_cours is None:
                options.append("Nouvelle vente")
            else:
                print(f"Vente en cours: #{self.vente_en_cours}")
                options.append("Ajouter un produit à la vente")
                options.append("Finaliser la vente")
                options.append("Annuler la vente en cours")
        
        options.append("Rechercher un produit")
        options.append("Retour de produits")
        options.append("Quitter")
        
        for i, option in enumerate(options[:-1], 1):
            print(f"{i}. {option}")
        
        print(f"0. {options[-1]}")
        print("-" * 40)
        
        return options
    
    def selectionner_caisse(self):
        """Permet à l'utilisateur de sélectionner une caisse"""
        print("\n--- Sélection d'une caisse ---")
        print("Caisses disponibles:")
        print("1. Caisse 1")
        print("2. Caisse 2")
        print("3. Caisse 3")
        
        choix = input("Sélectionnez une caisse (1-3): ")
        if choix in ['1', '2', '3']:
            self.caisse_id = int(choix)
            print(f"Caisse {self.caisse_id} sélectionnée.")
        else:
            print("Choix invalide.")
    
    def demarrer_vente(self):
        """Démarre une nouvelle vente"""
        if self.caisse_id is None:
            print("Veuillez d'abord sélectionner une caisse.")
            return
        
        if self.vente_en_cours is not None:
            print(f"Une vente est déjà en cours (#{self.vente_en_cours}).")
            return
        
        vente_id = VenteService.demarrer_vente(self.caisse_id)
        if vente_id:
            self.vente_en_cours = vente_id
            print(f"Nouvelle vente démarrée (#{vente_id}).")
        else:
            print("Erreur lors de la création de la vente.")
    
    def ajouter_produit_vente(self):
        """Ajoute un produit à la vente en cours"""
        if self.vente_en_cours is None:
            print("Aucune vente en cours.")
            return
        
        terme = input("Rechercher un produit (ID, code ou nom): ")
        produits = ProduitService.rechercher_produit(terme)
        
        if not produits:
            print("Aucun produit trouvé.")
            return
        
        self.afficher_produits(produits)
        
        choix = input("\nEntrez l'ID du produit à ajouter (ou 0 pour annuler): ")
        if choix == '0' or not choix:
            return
        
        try:
            produit_id = int(choix)
            produit_existe = False
            for p in produits:
                if p["id"] == produit_id:
                    produit_existe = True
                    break
            
            if not produit_existe:
                print("Produit non trouvé dans les résultats.")
                return
            
            quantite = input("Quantité (défaut: 1): ")
            quantite = int(quantite) if quantite.strip() else 1
            
            succes, message = VenteService.ajouter_produit(self.vente_en_cours, produit_id, quantite)
            print(message)
            
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    def finaliser_vente(self):
        """Finalise la vente en cours et affiche le reçu"""
        if self.vente_en_cours is None:
            print("Aucune vente en cours.")
            return
        
        succes, resultat = VenteService.finaliser_vente(self.vente_en_cours)
        if succes:
            self.afficher_recu(resultat)
            self.vente_en_cours = None
        else:
            print(f"Erreur: {resultat.get('erreur', 'Erreur inconnue')}")
    
    def annuler_vente_en_cours(self):
        """Annule la vente en cours"""
        if self.vente_en_cours is None:
            print("Aucune vente en cours.")
            return
        
        self.vente_en_cours = None
        print("Vente en cours annulée.")
    
    def effectuer_retour_produits(self):
        """Interface pour effectuer un retour de produits"""
        print("\n--- Retour de produits ---")
        
        if self.vente_en_cours is not None:
            print(f"Une vente est actuellement en cours (#{self.vente_en_cours}).")
            choix = input("Voulez-vous annuler cette vente et retourner les produits? (o/n): ")
            if choix.lower() == 'o':
                self.annuler_vente_en_cours()
                return
        
        vente_id = input("Entrez l'ID de la vente pour le retour (ou 0 pour annuler): ")
        if vente_id == '0' or not vente_id.strip():
            return
        
        try:
            vente_id = int(vente_id)
            
            confirmation = input(f"Confirmer le retour de la vente #{vente_id}? (o/n): ")
            if confirmation.lower() != 'o':
                print("Retour annulé.")
                return
            
            succes, message = VenteService.effectuer_retour(vente_id)
            print(message)
            
            if self.vente_en_cours == vente_id:
                self.vente_en_cours = None
        
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    def rechercher_produit(self):
        """Interface de recherche de produits"""
        print("\n--- Recherche de produits ---")
        print("1. Recherche par ID/nom/code")
        print("2. Recherche par catégorie")
        print("0. Retour au menu principal")
        
        choix = input("Votre choix: ")
        
        if choix == '0':
            return
        elif choix == '1':
            terme = input("Terme de recherche: ")
            produits = ProduitService.rechercher_produit(terme)
            self.afficher_produits(produits)
        
        elif choix == '2':
            categories = CategorieService.liste_categories()
            print("\nCatégories disponibles:")
            for cat in categories:
                print(f"{cat['id']}. {cat['nom']}")
            
            try:
                categorie_id = input("\nEntrez l'ID de la catégorie: ")
                if not categorie_id.strip() or not categorie_id.isdigit():
                    categorie_nom = input("Ou entrez le nom de la catégorie: ")
                    produits = ProduitService.rechercher_par_categorie(categorie_nom)
                else:
                    categorie_id = int(categorie_id)
                    categorie_existe = False
                    categorie_nom = ""
                    
                    for cat in categories:
                        if cat['id'] == categorie_id:
                            categorie_existe = True
                            categorie_nom = cat['nom']
                            break
                    
                    if not categorie_existe:
                        print(f"Catégorie avec ID {categorie_id} introuvable.")
                        return
                    
                    produits = ProduitService.rechercher_par_categorie(categorie_nom)
                
                self.afficher_produits(produits)
            except ValueError:
                print("Veuillez entrer un nombre valide pour l'ID de la catégorie.")
        
        else:
            print("Choix invalide.")
    
    def afficher_categories(self):
        """Affiche la liste des catégories disponibles"""
        categories = CategorieService.liste_categories()
        
        print("\n--- Liste des catégories ---")
        for cat in categories:
            print(f"{cat['id']}. {cat['nom']} - {cat['description']}")
    
    def afficher_produits(self, produits: List[Dict[str, Any]]):
        """Affiche une liste formatée de produits"""
        if not produits:
            print("Aucun produit trouvé.")
            return
        
        print("\n--- Résultats de la recherche ---")
        print(f"{'ID':<4} | {'Code':<8} | {'Nom':<20} | {'Prix':<8} | {'Stock':<6} | {'Catégorie':<15}")
        print("-" * 70)
        
        for p in produits:
            print(f"{p['id']:<4} | {p['code']:<8} | {p['nom']:<20} | {p['prix']:<8.2f} | {p['stock']:<6} | {p['categorie']:<15}")
    
    def afficher_recu(self, vente: Dict[str, Any]):
        """Affiche un reçu formaté pour la vente"""
        print("\n" + "=" * 40)
        print(f"REÇU DE VENTE #{vente['vente_id']}")
        print(f"Date: {vente['date']}")
        print(f"Caisse: {vente['caisse']}")
        print("-" * 40)
        
        print(f"{'Produit':<25} | {'Qté':<4} | {'Prix':<8} | {'Total':<8}")
        print("-" * 40)
        
        for ligne in vente['lignes']:
            print(f"{ligne['produit']:<25} | {ligne['quantite']:<4} | {ligne['prix_unitaire']:<8.2f} | {ligne['sous_total']:<8.2f}")
        
        print("-" * 40)
        print(f"TOTAL: {vente['total']:.2f} €")
        print("=" * 40)
    
    def executer(self):
        """Exécute l'application en boucle"""
        while True:
            options = self.afficher_menu_principal()
            choix = input("Votre choix: ")
            
            if choix == '0':
                print("Au revoir!")
                break
            
            try:
                choix_num = int(choix)
                if 1 <= choix_num <= len(options) - 1:  # -1 car "Quitter" est toujours à la fin

                    # Déterminer quelle action exécuter en fonction du choix et de l'état courant
                    action = options[choix_num - 1]  # -1 car les indices commencent à 0
                    
                    if action == "Sélectionner une caisse":
                        self.selectionner_caisse()
                    elif action == "Nouvelle vente":
                        self.demarrer_vente()
                    elif action == "Ajouter un produit à la vente":
                        self.ajouter_produit_vente()
                    elif action == "Finaliser la vente":
                        self.finaliser_vente()
                    elif action == "Annuler la vente en cours":
                        self.annuler_vente_en_cours()
                    elif action == "Rechercher un produit":
                        self.rechercher_produit()
                    elif action == "Retour de produits":
                        self.effectuer_retour_produits()
                else:
                    print("Option invalide.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
            os.system('cls' if os.name == 'nt' else 'clear')


def main():
    # Initialise la DB seulement si elle n'existe pas
    initialize_db()

    try:
        app = CaisseMagasinApp()
        app.executer()
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUne erreur est survenue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
   main()
