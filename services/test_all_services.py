#!/usr/bin/env python3
"""
Script de test simple pour vérifier que tous les microservices peuvent être importés
"""

import sys
import os

def test_service(service_name, service_path):
    """Test simple d'import d'un service"""
    print(f"🔄 Test de {service_name}...")
    
    try:
        # Ajouter le chemin du service au PYTHONPATH
        sys.path.insert(0, os.path.join(service_path, 'src'))
        
        # Essayer d'importer l'app
        from main import app
        
        # Compter les routes
        route_count = len(app.routes)
        
        print(f"✅ {service_name} - App créée avec succès ({route_count} routes)")
        return True
        
    except Exception as e:
        print(f"❌ {service_name} - Erreur: {str(e)}")
        return False
    finally:
        # Nettoyer le PYTHONPATH
        if os.path.join(service_path, 'src') in sys.path:
            sys.path.remove(os.path.join(service_path, 'src'))

def main():
    """Test principal de tous les services"""
    print("🚀 Test de tous les microservices")
    print("=" * 50)
    
    services = [
        ("Reporting API", "reporting-api"),
        ("Inventory API", "inventory-api"),
        ("Ecommerce API", "ecommerce-api"),
        ("Retail API", "retail-api")
    ]
    
    results = []
    
    for service_name, service_path in services:
        success = test_service(service_name, service_path)
        results.append((service_name, success))
        print()
    
    # Résumé
    print("📊 Résumé des tests:")
    print("=" * 30)
    
    successful = 0
    for service_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {service_name}: {status}")
        if success:
            successful += 1
    
    print(f"\n🎯 Résultat: {successful}/{len(services)} services fonctionnent")
    
    if successful == len(services):
        print("🎉 Tous les services fonctionnent parfaitement!")
    elif successful >= len(services) // 2:
        print("👍 La majorité des services fonctionnent")
    else:
        print("⚠️ Plusieurs services ont des problèmes")

if __name__ == "__main__":
    main() 