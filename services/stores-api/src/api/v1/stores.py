from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database import get_db
from ...schemas import StoreCreate, StoreUpdate, StoreResponse, StorePage
from ...services import StoreService

router = APIRouter()

def get_store_service(db: Session = Depends(get_db)) -> StoreService:
    return StoreService(db)

@router.get("/", response_model=StorePage)
def read_stores(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(default=None, description="Search in store names"),
    store_service: StoreService = Depends(get_store_service),
):
    """Retrieve stores with pagination, sorting, and filtering."""
    return store_service.get_stores_paginated(page=page, size=size, search=search)

@router.get("/{store_id}", response_model=StoreResponse)
def read_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
):
    """Get store by ID."""
    store = store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
    return store

@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(
    store: StoreCreate,
    store_service: StoreService = Depends(get_store_service),
):
    """Create new store."""
    try:
        return store_service.create_store(store)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store: StoreUpdate,
    store_service: StoreService = Depends(get_store_service),
):
    """Update a store completely."""
    try:
        updated_store = store_service.update_store(store_id, store)
        if not updated_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return updated_store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{store_id}", response_model=StoreResponse)
def partial_update_store(
    store_id: int,
    store: StoreUpdate,
    store_service: StoreService = Depends(get_store_service),
):
    """Partially update a store."""
    try:
        updated_store = store_service.update_store(store_id, store)
        if not updated_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return updated_store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
):
    """Delete a store."""
    # First get the store to return it
    store = store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")

    # Then delete it
    try:
        deleted = store_service.delete_store(store_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Business endpoints
@router.get("/by-name/{name}", response_model=StoreResponse)
def get_store_by_name(
    name: str,
    store_service: StoreService = Depends(get_store_service),
):
    """Get store by name."""
    store = store_service.get_store_by_name(name)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with name '{name}' not found")
    return store

@router.post("/{store_id}/update-contact", response_model=StoreResponse)
def update_store_contact(
    store_id: int,
    email: Optional[str] = None,
    telephone: Optional[str] = None,
    store_service: StoreService = Depends(get_store_service),
):
    """Update store contact information."""
    try:
        updated_store = store_service.update_store_contact(store_id, email, telephone)
        if not updated_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return updated_store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/with-contact/", response_model=List[StoreResponse])
def get_stores_with_contact(
    store_service: StoreService = Depends(get_store_service),
):
    """Get stores that have at least email or phone contact information."""
    return store_service.get_stores_with_contact()

@router.get("/business/complete-contact", response_model=List[StoreResponse])
def get_stores_with_complete_contact(
    store_service: StoreService = Depends(get_store_service),
):
    """Get stores with complete contact information (email, phone, and address)."""
    return store_service.get_stores_with_complete_contact() 