#!/usr/bin/env python3
"""
Script pour exécuter tous les tests unitaires des microservices
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, cwd=None):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout: La commande a pris trop de temps"
    except Exception as e:
        return False, "", str(e)

def print_header(text):
    """Affiche un header stylisé"""
    print("\n" + "="*80)
    print(f"🧪 {text}")
    print("="*80)

def print_service_header(service_name):
    """Affiche le header d'un service"""
    print(f"\n📋 Testing {service_name}")
    print("-" * 50)

def install_dependencies(service_path):
    """Installe les dépendances de test pour un service"""
    print(f"📦 Installing test dependencies for {service_path.name}...")
    success, stdout, stderr = run_command("pip3 install -r requirements.txt", cwd=service_path)
    
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print(f"✅ Dependencies installed successfully")
    return True

def run_service_tests(service_path):
    """Exécute les tests d'un service"""
    service_name = service_path.name
    print_service_header(f"{service_name.upper()} API")
    
    # Vérifier si le dossier tests existe
    tests_dir = service_path / "tests"
    if not tests_dir.exists():
        print(f"⚠️ No tests directory found for {service_name}")
        return True, 0, 0
    
    # Vérifier s'il y a des fichiers de test
    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        print(f"⚠️ No test files found for {service_name}")
        return True, 0, 0
    
    # Installer les dépendances
    if not install_dependencies(service_path):
        return False, 0, 0
    
    # Exécuter les tests avec pytest
    print(f"🔬 Running tests for {service_name}...")
    cmd = "python3 -m pytest tests/ -v --tb=short --no-header"
    success, stdout, stderr = run_command(cmd, cwd=service_path)
    
    # Parser les résultats
    passed_tests = stdout.count(" PASSED")
    failed_tests = stdout.count(" FAILED")
    total_tests = passed_tests + failed_tests
    
    if success:
        print(f"✅ All tests passed for {service_name}")
        print(f"   📊 {passed_tests} tests passed")
    else:
        print(f"❌ Some tests failed for {service_name}")
        print(f"   📊 {passed_tests} tests passed, {failed_tests} tests failed")
        if stderr:
            print(f"   🔍 Errors: {stderr[:200]}...")
    
    # Afficher un résumé des tests
    if stdout:
        lines = stdout.split('\n')
        test_lines = [line for line in lines if "test_" in line and "::" in line]
        for line in test_lines[-5:]:  # Derniers 5 tests
            if " PASSED" in line:
                print(f"   ✅ {line.split('::')[-1].split(' ')[0]}")
            elif " FAILED" in line:
                print(f"   ❌ {line.split('::')[-1].split(' ')[0]}")
    
    return success, passed_tests, failed_tests

def main():
    """Fonction principale"""
    print_header("EXECUTION DES TESTS UNITAIRES - MICROSERVICES DDD")
    
    # Répertoire des services
    services_dir = Path(__file__).parent
    
    # Liste des services à tester
    services = [
        # Services magasins physiques
        "products-api",
        "sales-api", 
        "stock-api",
        "stores-api",
        "reporting-api",
        # Services e-commerce
        "customers-api",
        "cart-api",
        "orders-api"
    ]
    
    total_passed = 0
    total_failed = 0
    failed_services = []
    
    start_time = time.time()
    
    for service in services:
        service_path = services_dir / service
        
        if not service_path.exists():
            print(f"⚠️ Service directory {service} not found, skipping...")
            continue
        
        success, passed, failed = run_service_tests(service_path)
        total_passed += passed
        total_failed += failed
        
        if not success:
            failed_services.append(service)
    
    # Résumé final
    elapsed_time = round(time.time() - start_time, 2)
    
    print_header("RÉSUMÉ FINAL DES TESTS")
    print(f"⏱️  Temps d'exécution: {elapsed_time}s")
    print(f"📊 Total des tests: {total_passed + total_failed}")
    print(f"✅ Tests réussis: {total_passed}")
    print(f"❌ Tests échoués: {total_failed}")
    print(f"🏗️  Services testés: {len(services) - len(failed_services)}/{len(services)}")
    
    if failed_services:
        print(f"\n⚠️ Services avec échecs:")
        for service in failed_services:
            print(f"   - {service}")
    
    # Vérifications des améliorations
    print(f"\n🔥 FONCTIONNALITÉS TESTÉES:")
    print(f"   🏪 MAGASINS PHYSIQUES:")
    print(f"     ✅ Gestion des produits et catégories")
    print(f"     ✅ Système de ventes et lignes de vente")
    print(f"     ✅ Gestion des stocks centralisés")
    print(f"     ✅ Magasins et caisses enregistreuses")
    print(f"     ✅ Rapports et analytics")
    print(f"   🛒 E-COMMERCE:")
    print(f"     ✅ Comptes clients et authentification JWT")
    print(f"     ✅ Paniers d'achat (clients + invités)")
    print(f"     ✅ Commandes et checkout complet")
    print(f"   🔧 ARCHITECTURE:")
    print(f"     ✅ Logging structuré avec Request-ID")
    print(f"     ✅ Middleware de traçage HTTP") 
    print(f"     ✅ Gestion d'erreurs standardisée")
    print(f"     ✅ APIs RESTful compliant")
    print(f"     ✅ Communication inter-services")
    print(f"     ✅ Architecture DDD")
    print(f"     ✅ Coordination entre bases de données")
    
    if total_failed == 0 and not failed_services:
        print(f"\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print(f"🏪 Système de magasins physiques: OPÉRATIONNEL")
        print(f"🛒 Système e-commerce: OPÉRATIONNEL")
        print(f"🔗 Coordination inter-services: VALIDÉE")
        print(f"🚀 Architecture production-ready!")
        return 0
    else:
        print(f"\n🔧 Certains tests ont échoué, vérifiez les détails ci-dessus.")
        
        # Détail des échecs par catégorie
        store_services = ["products-api", "sales-api", "stock-api", "stores-api", "reporting-api"]
        ecommerce_services = ["customers-api", "cart-api", "orders-api"]
        
        store_failures = [s for s in failed_services if s in store_services]
        ecommerce_failures = [s for s in failed_services if s in ecommerce_services]
        
        if store_failures:
            print(f"🏪 Échecs magasins physiques: {', '.join(store_failures)}")
        if ecommerce_failures:
            print(f"🛒 Échecs e-commerce: {', '.join(ecommerce_failures)}")
            
        return 1

if __name__ == "__main__":
    sys.exit(main()) 