from typing import List, Optional
from ..entities.product import Product
from ..repositories.product_repository import ProductRepositoryInterface
from ..schemas.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductPage,
)


class ProductService:
    """Application service for Product domain operations"""

    def __init__(self, product_repository: ProductRepositoryInterface):
        self.product_repository = product_repository

    def get_product_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """Get a product by its ID"""
        product = self.product_repository.get_by_id(product_id)
        if product:
            return self._to_response(product)
        return None

    def get_product_by_code(self, code: str) -> Optional[ProductResponse]:
        """Get a product by its code"""
        product = self.product_repository.get_by_code(code)
        if product:
            return self._to_response(product)
        return None

    def get_products_paginated(self, page: int = 1, size: int = 20) -> ProductPage:
        """Get paginated list of products"""
        skip = (page - 1) * size
        products = self.product_repository.get_all(skip=skip, limit=size)
        total = self.product_repository.count()

        return ProductPage(
            total=total,
            page=page,
            size=size,
            items=[self._to_response(product) for product in products],
        )

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product with business validation"""
        # Check if product code already exists
        existing_product = self.product_repository.get_by_code(product_data.code)
        if existing_product:
            raise ValueError(f"Product with code '{product_data.code}' already exists")

        # Create the product
        product = self.product_repository.create(product_data)
        return self._to_response(product)

    def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """Update an existing product with business validation"""
        # Check if product exists
        existing_product = self.product_repository.get_by_id(product_id)
        if not existing_product:
            return None

        # Check if new code conflicts with another product
        if product_data.code and product_data.code != existing_product.code:
            code_conflict = self.product_repository.get_by_code(product_data.code)
            if code_conflict and code_conflict.id != product_id:
                raise ValueError(
                    f"Product with code '{product_data.code}' already exists"
                )

        # Update the product
        updated_product = self.product_repository.update(product_id, product_data)
        if updated_product:
            return self._to_response(updated_product)
        return None

    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        # Additional business logic could go here
        # e.g., check if product is used in any orders
        return self.product_repository.delete(product_id)

    def reduce_product_stock(
        self, product_id: int, quantity: int
    ) -> Optional[ProductResponse]:
        """Reduce product stock (business operation)"""
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        # Apply business logic using entity methods
        product.reduce_stock(quantity)

        # Update in repository
        update_data = ProductUpdate(quantite_stock=product.quantite_stock)
        updated_product = self.product_repository.update(product_id, update_data)
        if updated_product:
            return self._to_response(updated_product)
        return None

    def increase_product_stock(
        self, product_id: int, quantity: int
    ) -> Optional[ProductResponse]:
        """Increase product stock (business operation)"""
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        # Apply business logic using entity methods
        product.increase_stock(quantity)

        # Update in repository
        update_data = ProductUpdate(quantite_stock=product.quantite_stock)
        updated_product = self.product_repository.update(product_id, update_data)
        if updated_product:
            return self._to_response(updated_product)
        return None

    def get_low_stock_products(self, threshold: int = 10) -> List[ProductResponse]:
        """Get products with low stock (business query)"""
        all_products = self.product_repository.get_all(
            limit=1000
        )  # Consider pagination for large datasets
        low_stock_products = [
            product for product in all_products if product.quantite_stock <= threshold
        ]
        return [self._to_response(product) for product in low_stock_products]

    def _to_response(self, product: Product) -> ProductResponse:
        """Convert domain entity to response schema"""
        return ProductResponse(
            id=product.id,
            code=product.code,
            nom=product.nom,
            description=product.description,
            prix=product.prix,
            quantite_stock=product.quantite_stock,
            categorie_id=product.categorie_id,
        )
