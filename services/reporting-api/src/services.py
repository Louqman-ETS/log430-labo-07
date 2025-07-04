from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import math
import httpx
from datetime import datetime, date

from src.schemas import (
    GlobalSummaryResponse,
    StorePerformanceResponse,
    TopProductResponse,
)
from src.external_services import external_client


class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    async def get_global_summary(self) -> GlobalSummaryResponse:
        """Get global business summary using data from all services"""
        # Get sales data from retail-api
        try:
            async with httpx.AsyncClient() as client:
                sales_response = await client.get(
                    f"{external_client.retail_api_url}/sales/"
                )
                if sales_response.status_code == 200:
                    sales_data = sales_response.json()
                    total_sales = len(sales_data)
                    total_revenue = sum(sale.get("total", 0) for sale in sales_data)
                    average_sale_amount = (
                        total_revenue / total_sales if total_sales > 0 else 0.0
                    )
                else:
                    total_sales = 0
                    total_revenue = 0.0
                    average_sale_amount = 0.0
        except Exception as e:
            print(f"Error fetching sales from retail-api: {e}")
            total_sales = 0
            total_revenue = 0.0
            average_sale_amount = 0.0

        # Get data from external services
        products = await external_client.get_products(page=1, size=1000)
        stores = await external_client.get_stores(page=1, size=1000)

        return GlobalSummaryResponse(
            total_sales=total_sales,
            total_revenue=float(total_revenue),
            total_products=len(products or []),
            total_stores=len(stores or []),
            average_sale_amount=float(average_sale_amount),
        )

    async def get_store_performances(self) -> List[StorePerformanceResponse]:
        """Get performance metrics for all stores"""
        # Get sales data from retail-api
        try:
            async with httpx.AsyncClient() as client:
                sales_response = await client.get(
                    f"{external_client.retail_api_url}/sales/"
                )
                if sales_response.status_code == 200:
                    sales_data = sales_response.json()
                else:
                    sales_data = []
        except Exception as e:
            print(f"Error fetching sales from retail-api: {e}")
            sales_data = []

        # Group sales by store
        store_sales = {}
        for sale in sales_data:
            store_id = sale.get("store_id")
            if store_id not in store_sales:
                store_sales[store_id] = {
                    "sales_count": 0,
                    "revenue": 0.0,
                    "amounts": [],
                }
            store_sales[store_id]["sales_count"] += 1
            store_sales[store_id]["revenue"] += sale.get("total", 0)
            store_sales[store_id]["amounts"].append(sale.get("total", 0))

        # Get store information from external service
        stores = await external_client.get_stores(page=1, size=1000)
        stores_dict = {store["id"]: store for store in stores}

        performances = []
        for store_id, sales_info in store_sales.items():
            store_info = stores_dict.get(store_id, {})

            # Calculate average sale amount
            avg_amount = (
                sum(sales_info["amounts"]) / len(sales_info["amounts"])
                if sales_info["amounts"]
                else 0.0
            )

            # Calculate performance rating
            revenue = float(sales_info["revenue"])
            if revenue > 10000:
                rating = "Excellent"
            elif revenue > 5000:
                rating = "Good"
            elif revenue > 2000:
                rating = "Average"
            else:
                rating = "Below Average"

            performances.append(
                StorePerformanceResponse(
                    store_id=store_id,
                    store_name=store_info.get("nom", f"Store {store_id}"),
                    sales_count=sales_info["sales_count"],
                    revenue=revenue,
                    average_sale_amount=avg_amount,
                    performance_rating=rating,
                )
            )

        return sorted(performances, key=lambda x: x.revenue, reverse=True)

    async def get_top_products(self, limit: int = 10) -> List[TopProductResponse]:
        """Get top performing products"""
        # Get sales data from retail-api
        try:
            async with httpx.AsyncClient() as client:
                sales_response = await client.get(
                    f"{external_client.retail_api_url}/sales/"
                )
                if sales_response.status_code == 200:
                    sales_data = sales_response.json()
                else:
                    sales_data = []
        except Exception as e:
            print(f"Error fetching sales from retail-api: {e}")
            sales_data = []

        # Group sales by product
        product_sales = {}
        for sale in sales_data:
            sale_lines = sale.get("sale_lines", [])
            for line in sale_lines:
                product_id = line.get("product_id")
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        "total_quantity": 0,
                        "total_revenue": 0.0,
                        "sales_count": 0,
                    }
                product_sales[product_id]["total_quantity"] += line.get("quantite", 0)
                product_sales[product_id]["total_revenue"] += line.get("sous_total", 0)
                product_sales[product_id]["sales_count"] += 1

        # Sort by revenue and get top products
        sorted_products = sorted(
            product_sales.items(), key=lambda x: x[1]["total_revenue"], reverse=True
        )[:limit]

        # Get product information from external service
        top_products = []
        for product_id, sales_info in sorted_products:
            product_info = await external_client.get_product(product_id)

            top_products.append(
                TopProductResponse(
                    product_id=product_id,
                    product_name=(
                        product_info.get("nom", f"Product {product_id}")
                        if product_info
                        else f"Product {product_id}"
                    ),
                    product_code=product_info.get("code", "") if product_info else "",
                    total_quantity_sold=sales_info["total_quantity"],
                    total_revenue=sales_info["total_revenue"],
                    sales_count=sales_info["sales_count"],
                )
            )

        return top_products

    async def get_store_performance(
        self, store_id: int
    ) -> Optional[StorePerformanceResponse]:
        """Get performance for a specific store"""
        # Verify store exists
        store_info = await external_client.get_store(store_id)
        if not store_info:
            return None

        # Get sales data for this store
        try:
            async with httpx.AsyncClient() as client:
                sales_response = await client.get(
                    f"{external_client.retail_api_url}/sales/"
                )
                if sales_response.status_code == 200:
                    sales_data = sales_response.json()
                else:
                    sales_data = []
        except Exception as e:
            print(f"Error fetching sales from retail-api: {e}")
            sales_data = []

        # Filter sales for this store
        store_sales = [sale for sale in sales_data if sale.get("store_id") == store_id]

        if not store_sales:
            return StorePerformanceResponse(
                store_id=store_id,
                store_name=store_info.get("nom", f"Store {store_id}"),
                sales_count=0,
                revenue=0.0,
                average_sale_amount=0.0,
                performance_rating="No Sales",
            )

        # Calculate metrics
        total_revenue = sum(sale.get("total", 0) for sale in store_sales)
        avg_amount = total_revenue / len(store_sales) if store_sales else 0.0

        # Calculate performance rating
        if total_revenue > 10000:
            rating = "Excellent"
        elif total_revenue > 5000:
            rating = "Good"
        elif total_revenue > 2000:
            rating = "Average"
        else:
            rating = "Below Average"

        return StorePerformanceResponse(
            store_id=store_id,
            store_name=store_info.get("nom", f"Store {store_id}"),
            sales_count=len(store_sales),
            revenue=float(total_revenue),
            average_sale_amount=float(avg_amount),
            performance_rating=rating,
        )
