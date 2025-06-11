from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.v1 import crud
from src.app.api.v1.models import Store, StoreCreate, StoreUpdate, StorePage
from src.app.api.v1 import dependencies
from src.db import get_db

router = APIRouter(dependencies=[Depends(dependencies.api_token_auth)])


@router.get("", response_model=StorePage)
def read_stores(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> Any:
    """
    Retrieve stores with pagination.
    """
    stores = crud.get_stores(db, skip=(page - 1) * size, limit=size)
    total = crud.get_stores_count(db)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": stores,
    }


@router.post("", response_model=Store, status_code=status.HTTP_201_CREATED)
def create_store(
    *,
    db: Session = Depends(get_db),
    store_in: StoreCreate,
) -> Any:
    """
    Create new store.
    """
    store = crud.create_store(db, obj_in=store_in)
    return store


@router.get("/{store_id}", response_model=Store)
def read_store(
    *,
    db: Session = Depends(get_db),
    store_id: int,
) -> Any:
    """
    Get store by ID.
    """
    store = crud.get_store(db, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/{store_id}", response_model=Store)
def update_store(
    *,
    db: Session = Depends(get_db),
    store_id: int,
    store_in: StoreUpdate,
) -> Any:
    """
    Update a store.
    """
    store = crud.get_store(db, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store = crud.update_store(db, db_obj=store, obj_in=store_in)
    return store


@router.delete("/{store_id}", response_model=Store)
def delete_store(
    *,
    db: Session = Depends(get_db),
    store_id: int,
) -> Any:
    """
    Delete a store.
    """
    store = crud.get_store(db, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store = crud.delete_store(db, db_obj=store)
    return store
