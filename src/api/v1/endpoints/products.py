from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db import get_db
from ..dependencies import api_token_auth
from ..errors import NotFoundError, DuplicateError, BusinessLogicError
from ..services.cache_service import cache_service, cache_key_for_request

from ..domain.products.entities.product import Product
from ..domain.products.repositories.product_repository import ProductRepository
from ..domain.products.services.product_service import ProductService
from ..domain.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductPage,
)

router = APIRouter()


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency injection for ProductService"""
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


@router.get("/", response_model=ProductPage)
async def read_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        default="id,asc", description="Sort by field and order (field,asc|desc)"
    ),
    search: Optional[str] = Query(
        default=None, description="Search in product names and codes"
    ),
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Retrieve products with pagination, sorting, and filtering."""
    # Cache key pour cette requête
    cache_key = cache_key_for_request("products", {
        "page": page, "size": size, "sort": sort, "search": search
    })
    
    # Vérifier le cache d'abord
    cached_result = cache_service.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Si pas en cache, récupérer les données
    result = product_service.get_products_paginated(page=page, size=size)
    
    # Mettre en cache pour 2 minutes (endpoint souvent consulté)
    cache_service.set(cache_key, result, ttl=120)
    
    return result


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Get product by ID."""
    # Cache key pour ce produit spécifique
    cache_key = cache_key_for_request("product", {"id": product_id})
    
    # Vérifier le cache d'abord
    cached_result = cache_service.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Si pas en cache, récupérer le produit
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise NotFoundError("Product", product_id)
    
    # Mettre en cache pour 5 minutes (données de produit changent peu)
    cache_service.set(cache_key, product, ttl=300)
    
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Create new product."""
    try:
        return product_service.create_product(product)
    except ValueError as e:
        raise DuplicateError("Product", "code", product.code)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Update a product completely."""
    try:
        updated_product = product_service.update_product(product_id, product)
        if not updated_product:
            raise NotFoundError("Product", product_id)
        return updated_product
    except ValueError as e:
        if "already exists" in str(e):
            raise DuplicateError("Product", "code", product.code)
        raise BusinessLogicError(str(e))


@router.patch("/{product_id}", response_model=ProductResponse)
async def partial_update_product(
    product_id: int,
    product: ProductUpdate,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Partially update a product."""
    try:
        updated_product = product_service.update_product(product_id, product)
        if not updated_product:
            raise NotFoundError("Product", product_id)
        return updated_product
    except ValueError as e:
        if "already exists" in str(e):
            raise DuplicateError("Product", "code", product.code or "")
        raise BusinessLogicError(str(e))


@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: int,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Delete a product."""
    # First get the product to return it
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise NotFoundError("Product", product_id)

    # Then delete it
    deleted = product_service.delete_product(product_id)
    if not deleted:
        raise NotFoundError("Product", product_id)

    return product


# Business endpoints
@router.post("/{product_id}/reduce-stock", response_model=ProductResponse)
async def reduce_product_stock(
    product_id: int,
    quantity: int = Query(..., ge=1, description="Quantity to reduce"),
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Reduce product stock (business operation)."""
    try:
        updated_product = product_service.reduce_product_stock(product_id, quantity)
        if not updated_product:
            raise NotFoundError("Product", product_id)
        return updated_product
    except ValueError as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Product", product_id)
        raise BusinessLogicError(str(e))


@router.get("/low-stock/", response_model=List[ProductResponse])
async def get_low_stock_products(
    threshold: int = Query(default=10, ge=0, description="Stock threshold"),
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Get products with low stock."""
    return product_service.get_low_stock_products(threshold)


@router.get("/by-code/{code}", response_model=ProductResponse)
async def get_product_by_code(
    code: str,
    _: str = Depends(api_token_auth),  # Authentification requise
    product_service: ProductService = Depends(get_product_service),
):
    """Get product by code."""
    product = product_service.get_product_by_code(code)
    if not product:
        raise NotFoundError("Product", code)
    return product
