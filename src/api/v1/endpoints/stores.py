from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from src.db import get_db
from ..dependencies import api_token_auth
from ..errors import NotFoundError, DuplicateError, BusinessLogicError
from src.api.logging_config import (
    get_logger,
    log_business_operation,
    log_error_with_context,
)

from ..domain.stores.entities.store import Store
from ..domain.stores.repositories.store_repository import StoreRepository
from ..domain.stores.services.store_service import StoreService
from ..domain.stores.schemas.store_schemas import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    StorePage,
)

router = APIRouter()
logger = get_logger("api.endpoints.stores")


def get_store_service(db: Session = Depends(get_db)) -> StoreService:
    """Dependency injection pour le service Store"""
    store_repository = StoreRepository(db)
    return StoreService(store_repository)


@router.get("/", response_model=StorePage)
def read_stores(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Page size"),
    sort: Optional[str] = Query(
        default="id,asc", description="Sort by field and order (field,asc|desc)"
    ),
    search: Optional[str] = Query(default=None, description="Search in store names"),
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Retrieve stores with pagination, sorting, and filtering."""
    logger.info(
        f"Retrieving stores with pagination: page={page}, size={size}, search={search}"
    )

    try:
        result = store_service.get_stores_paginated(page=page, size=size)
        logger.info(f"Successfully retrieved {result.total} stores")
        return result
    except Exception as e:
        log_error_with_context(
            logger, e, {"operation": "read_stores", "page": page, "size": size}
        )
        raise


@router.get("/{store_id}", response_model=StoreResponse)
def read_store(
    store_id: int,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Get store by ID."""
    store = store_service.get_store_by_id(store_id)
    if not store:
        raise NotFoundError("Store", store_id)
    return store


@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(
    store: StoreCreate,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Create new store."""
    logger.info(f"Creating new store: {store.nom}")

    try:
        result = store_service.create_store(store)
        log_business_operation(
            logger,
            operation="CREATE",
            entity="Store",
            entity_id=str(result.id),
            store_name=store.nom,
            address=store.adresse,
        )
        logger.info(f"Successfully created store with ID: {result.id}")
        return result
    except ValueError as e:
        log_error_with_context(
            logger,
            e,
            {
                "operation": "create_store",
                "store_name": store.nom,
                "error_type": "business_logic",
            },
        )
        if "already exists" in str(e):
            raise DuplicateError("Store", "name", store.nom)
        raise BusinessLogicError(str(e))


@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store: StoreUpdate,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Update a store completely."""
    try:
        updated_store = store_service.update_store(store_id, store)
        if not updated_store:
            raise NotFoundError("Store", store_id)
        return updated_store
    except ValueError as e:
        if "already exists" in str(e):
            raise DuplicateError("Store", "name", store.nom or "")
        raise BusinessLogicError(str(e))


@router.patch("/{store_id}", response_model=StoreResponse)
def partial_update_store(
    store_id: int,
    store: StoreUpdate,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Partially update a store."""
    try:
        updated_store = store_service.update_store(store_id, store)
        if not updated_store:
            raise NotFoundError("Store", store_id)
        return updated_store
    except ValueError as e:
        if "already exists" in str(e):
            raise DuplicateError("Store", "name", store.nom or "")
        raise BusinessLogicError(str(e))


@router.delete("/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: int,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Delete a store."""
    logger.info(f"Deleting store with ID: {store_id}")

    try:
        # First get the store to return it
        store = store_service.get_store_by_id(store_id)
        if not store:
            logger.warning(f"Store not found for deletion: {store_id}")
            raise NotFoundError("Store", store_id)

        # Then delete it
        deleted = store_service.delete_store(store_id)
        if not deleted:
            logger.error(f"Failed to delete store: {store_id}")
            raise NotFoundError("Store", store_id)

        log_business_operation(
            logger,
            operation="DELETE",
            entity="Store",
            entity_id=str(store_id),
            store_name=store.nom,
        )
        logger.info(f"Successfully deleted store: {store_id}")
        return store
    except Exception as e:
        if not isinstance(e, (NotFoundError, DuplicateError, BusinessLogicError)):
            log_error_with_context(
                logger, e, {"operation": "delete_store", "store_id": store_id}
            )
        raise


# Business endpoints
@router.get("/by-name/{name}", response_model=StoreResponse)
def get_store_by_name(
    name: str,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Get store by name."""
    store = store_service.get_store_by_name(name)
    if not store:
        raise NotFoundError("Store", name)
    return store


@router.post("/{store_id}/update-contact", response_model=StoreResponse)
def update_store_contact(
    store_id: int,
    email: Optional[str] = None,
    telephone: Optional[str] = None,
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Update store contact information."""
    try:
        updated_store = store_service.update_store_contact(store_id, email, telephone)
        if not updated_store:
            raise NotFoundError("Store", store_id)
        return updated_store
    except ValueError as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Store", store_id)
        raise BusinessLogicError(str(e))


@router.get("/with-contact/", response_model=List[StoreResponse])
def get_stores_with_contact(
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Get stores that have contact information."""
    return store_service.get_stores_with_contact()


@router.get("/business/complete-contact", response_model=List[StoreResponse])
def get_stores_with_complete_contact(
    _: str = Depends(api_token_auth),  # Authentification requise
    store_service: StoreService = Depends(get_store_service),
):
    """Get stores with complete contact information - Business query using DDD"""
    try:
        return store_service.get_stores_with_complete_contact()
    except Exception as e:
        raise BusinessLogicError(str(e))
