from typing import Optional, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.v1 import crud
from src.api.v1.models import Product, ProductCreate, ProductUpdate, ProductPage
from src.api.v1 import dependencies
from src.db import get_db
from src.app.models.models import Produit as ProductModel

router = APIRouter(dependencies=[Depends(dependencies.api_token_auth)])


@router.get("", response_model=ProductPage)
def read_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        "id,asc", description="Sort by field and order (field,asc|desc)"
    ),
    category: Optional[str] = Query(None, description="Filter by category name"),
) -> Any:
    """
    Retrieve products with pagination, sorting, and filtering.
    """
    sort_field, sort_order = sort.split(",") if "," in sort else (sort, "asc")

    products = crud.get_products(
        db,
        skip=(page - 1) * size,
        limit=size,
        sort=sort_field,
        order=sort_order,
        category=category,
    )
    total = crud.get_products_count(db, category=category)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": products,
    }


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
) -> Any:
    """
    Create new product.
    """
    product = crud.create_product(db, obj_in=product_in)
    return product


@router.get("/{product_id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Get product by ID.
    """
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
) -> Any:
    """
    Update a product completely.
    """
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.update_product(db, db_obj=product, obj_in=product_in)
    return product


@router.patch("/{product_id}", response_model=Product)
def partial_update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
) -> Any:
    """
    Partially update a product.
    """
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.update_product(db, db_obj=product, obj_in=product_in)
    return product


@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Delete a product.
    """
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.delete_product(db, db_obj=product)
    return product
