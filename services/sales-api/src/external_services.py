import httpx
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExternalServiceClient:
    def __init__(self):
        self.products_api_url = os.getenv("PRODUCTS_API_URL", "http://products-api:8001/api/v1")
        self.stores_api_url = os.getenv("STORES_API_URL", "http://stores-api:8002/api/v1")
        self.stock_api_url = os.getenv("STOCK_API_URL", "http://stock-api:8004/api/v1")
        
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un produit depuis l'API Products"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.products_api_url}/products/{product_id}")
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Product {product_id} not found: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    async def get_store(self, store_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un magasin depuis l'API Stores"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.stores_api_url}/stores/{store_id}")
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Store {store_id} not found: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching store {store_id}: {e}")
            return None
    
    async def get_cash_register(self, cash_register_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'une caisse depuis l'API Stores"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.stores_api_url}/cash-registers/{cash_register_id}")
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Cash register {cash_register_id} not found: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching cash register {cash_register_id}: {e}")
            return None
    
    async def reduce_product_stock(self, product_id: int, quantity: int) -> bool:
        """Réduit le stock d'un produit via l'API Stock"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.stock_api_url}/products/{product_id}/stock/reduce?quantity={quantity}"
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error reducing stock for product {product_id}: {e}")
            return False
    
    async def validate_sale_data(self, store_id: int, cash_register_id: int, product_ids: list) -> Dict[str, Any]:
        """Valide toutes les données nécessaires pour créer une vente"""
        validation_result = {
            "valid": True,
            "errors": [],
            "store": None,
            "cash_register": None,
            "products": {}
        }
        
        # Valider le magasin
        store = await self.get_store(store_id)
        if not store:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Store {store_id} not found")
        else:
            validation_result["store"] = store
        
        # Valider la caisse enregistreuse
        cash_register = await self.get_cash_register(cash_register_id)
        if not cash_register:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Cash register {cash_register_id} not found")
        else:
            validation_result["cash_register"] = cash_register
        
        # Valider les produits
        for product_id in product_ids:
            product = await self.get_product(product_id)
            if not product:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Product {product_id} not found")
            else:
                validation_result["products"][product_id] = product
        
        return validation_result 