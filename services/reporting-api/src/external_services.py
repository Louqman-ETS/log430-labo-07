import httpx
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExternalServiceClient:
    """Client to communicate with other microservices"""
    
    def __init__(self):
        self.products_api_url = os.getenv("PRODUCTS_API_URL", "http://products-api:8001/api/v1")
        self.stores_api_url = os.getenv("STORES_API_URL", "http://stores-api:8002/api/v1")
        self.timeout = 30.0
    
    async def get_product(self, product_id: int) -> Optional[Dict[Any, Any]]:
        """Get product information from Products API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.products_api_url}/products/{product_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    async def get_products(self, page: int = 1, size: int = 100) -> List[Dict[Any, Any]]:
        """Get products list from Products API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.products_api_url}/products/",
                    params={"page": page, "size": size}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def get_store(self, store_id: int) -> Optional[Dict[Any, Any]]:
        """Get store information from Stores API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.stores_api_url}/stores/{store_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching store {store_id}: {e}")
            return None
    
    async def get_stores(self, page: int = 1, size: int = 100) -> List[Dict[Any, Any]]:
        """Get stores list from Stores API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.stores_api_url}/stores/",
                    params={"page": page, "size": size}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching stores: {e}")
            return []
    
    async def get_cash_register(self, register_id: int) -> Optional[Dict[Any, Any]]:
        """Get cash register information from Stores API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.stores_api_url}/cash-registers/{register_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching cash register {register_id}: {e}")
            return None
    
    async def reduce_product_stock(self, product_id: int, quantity: int) -> bool:
        """Reduce product stock via Products API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.products_api_url}/products/{product_id}/reduce-stock",
                    params={"quantity": quantity}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error reducing stock for product {product_id}: {e}")
            return False

# Global instance
external_client = ExternalServiceClient() 