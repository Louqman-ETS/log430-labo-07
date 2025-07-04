import httpx
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Configuration des services externes
INVENTORY_API_URL = os.getenv("INVENTORY_API_URL", "http://inventory-api:8001")


class ExternalServiceError(Exception):
    """Exception pour les erreurs de services externes"""

    pass


class InventoryService:
    """Service pour interagir avec l'API Inventory"""

    @staticmethod
    async def get_product_stock(product_id: int) -> Optional[Dict[str, Any]]:
        """Récupère le stock d'un produit"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{INVENTORY_API_URL}/api/v1/stock/products/{product_id}/stock"
                )

                if response.status_code == 404:
                    return None
                elif response.status_code != 200:
                    raise ExternalServiceError(
                        f"Inventory API error: {response.status_code}"
                    )

                return response.json()

        except httpx.RequestError as e:
            logger.error(f"❌ Erreur communication Inventory API: {str(e)}")
            raise ExternalServiceError(f"Cannot connect to Inventory API: {str(e)}")

    @staticmethod
    async def reduce_stock(
        product_id: int,
        quantity: int,
        reason: str = "vente",
        reference: Optional[str] = None,
    ) -> bool:
        """Réduit le stock d'un produit"""
        try:
            async with httpx.AsyncClient() as client:
                params = {"quantity": quantity, "raison": reason}
                if reference:
                    params["reference"] = reference

                response = await client.put(
                    f"{INVENTORY_API_URL}/api/v1/stock/products/{product_id}/stock/reduce",
                    params=params,
                )

                if response.status_code == 404:
                    logger.warning(f"⚠️ Product {product_id} not found in inventory")
                    return False
                elif response.status_code != 200:
                    raise ExternalServiceError(
                        f"Inventory API error: {response.status_code}"
                    )

                logger.info(f"✅ Stock reduced for product {product_id} by {quantity}")
                return True

        except httpx.RequestError as e:
            logger.error(f"❌ Erreur communication Inventory API: {str(e)}")
            raise ExternalServiceError(f"Cannot connect to Inventory API: {str(e)}")

    @staticmethod
    async def check_stock_availability(
        product_id: int, requested_quantity: int
    ) -> bool:
        """Vérifie si le stock est suffisant pour une quantité demandée"""
        try:
            stock_info = await InventoryService.get_product_stock(product_id)
            if not stock_info:
                return False

            available_stock = stock_info.get("quantite_stock", 0)
            return available_stock >= requested_quantity

        except Exception as e:
            logger.error(f"❌ Error checking stock availability: {str(e)}")
            return False
