from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database import get_db
from ...schemas import ProductCreate, ProductUpdate, ProductResponse, ProductPage
from ...services import ProductService

router = APIRouter()

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("/", response_model=ProductPage)
async def read_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(default=None, description="Search in product names and codes"),
    product_service: ProductService = Depends(get_product_service),
):
    """Retrieve products with pagination and filtering."""
    return product_service.get_products_paginated(page=page, size=size, search=search)

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """Get product by ID."""
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
):
    """Create new product."""
    try:
        return product_service.create_product(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
):
    """Update a product completely."""
    try:
        updated_product = product_service.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{product_id}", response_model=ProductResponse)
async def partial_update_product(
    product_id: int,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
):
    """Partially update a product."""
    try:
        updated_product = product_service.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """Delete a product."""
    # First get the product to return it
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    # Then delete it
    deleted = product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    return product

# Business endpoints
@router.post("/{product_id}/reduce-stock", response_model=ProductResponse)
async def reduce_product_stock(
    product_id: int,
    quantity: int = Query(..., ge=1, description="Quantity to reduce"),
    product_service: ProductService = Depends(get_product_service),
):
    """Reduce product stock (business operation)."""
    try:
        updated_product = product_service.reduce_product_stock(product_id, quantity)
        if not updated_product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/low-stock/", response_model=List[ProductResponse])
async def get_low_stock_products(
    threshold: int = Query(default=10, ge=0, description="Stock threshold"),
    product_service: ProductService = Depends(get_product_service),
):
    """Get products with low stock."""
    return product_service.get_low_stock_products(threshold)

@router.get("/by-code/{code}", response_model=ProductResponse)
async def get_product_by_code(
    code: str,
    product_service: ProductService = Depends(get_product_service),
):
    """Get product by code."""
    product = product_service.get_product_by_code(code)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with code '{code}' not found")
    return product 