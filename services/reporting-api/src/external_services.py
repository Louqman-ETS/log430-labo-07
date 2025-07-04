import httpx
import os
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExternalServiceClient:
    """Client to communicate with other microservices"""

    def __init__(self):
        self.inventory_api_url = os.getenv(
            "INVENTORY_API_URL", "http://inventory-api:8001/api/v1"
        )
        self.retail_api_url = os.getenv(
            "RETAIL_API_URL", "http://retail-api:8002/api/v1"
        )
        self.ecommerce_api_url = os.getenv(
            "ECOMMERCE_API_URL", "http://ecommerce-api:8000/api/v1"
        )
        self.timeout = 30.0

    async def get_product(self, product_id: int) -> Optional[Dict[Any, Any]]:
        """Get product information from Inventory API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.inventory_api_url}/products/{product_id}"
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None

    async def get_products(
        self, page: int = 1, size: int = 100
    ) -> List[Dict[Any, Any]]:
        """Get products list from Inventory API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.inventory_api_url}/products/",
                    params={"skip": (page - 1) * size, "limit": size},
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []

    async def get_store(self, store_id: int) -> Optional[Dict[Any, Any]]:
        """Get store information from Retail API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.retail_api_url}/stores/{store_id}")
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
        """Get stores list from Retail API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.retail_api_url}/stores/",
                    params={"skip": (page - 1) * size, "limit": size},
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error fetching stores: {e}")
            return []

    async def get_cash_register(self, register_id: int) -> Optional[Dict[Any, Any]]:
        """Get cash register information from Retail API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.retail_api_url}/cash-registers/{register_id}"
                )
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
        """Reduce product stock via Inventory API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.inventory_api_url}/stock/products/{product_id}/stock/reduce",
                    params={
                        "quantity": quantity,
                        "raison": "reporting_update",
                        "reference": "reporting",
                    },
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error reducing stock for product {product_id}: {e}")
            return False


# Global instance
external_client = ExternalServiceClient()
