from typing import List, Optional
import logging
from ..entities.store import Store
from ..repositories.store_repository import StoreRepositoryInterface
from ..schemas.store_schemas import StoreCreate, StoreUpdate, StoreResponse, StorePage
from src.api.logging_config import (
    get_logger,
    log_business_operation,
    log_error_with_context,
)


class StoreService:
    """Application service for Store domain operations"""

    def __init__(self, store_repository: StoreRepositoryInterface):
        self.store_repository = store_repository
        self.logger = get_logger("api.services.stores")

    def get_store_by_id(self, store_id: int) -> Optional[StoreResponse]:
        """Get a store by its ID"""
        store = self.store_repository.get_by_id(store_id)
        if store:
            return self._to_response(store)
        return None

    def get_store_by_name(self, name: str) -> Optional[StoreResponse]:
        """Get a store by its name"""
        store = self.store_repository.get_by_name(name)
        if store:
            return self._to_response(store)
        return None

    def get_stores_paginated(self, page: int = 1, size: int = 20) -> StorePage:
        """Get paginated list of stores"""
        skip = (page - 1) * size
        stores = self.store_repository.get_all(skip=skip, limit=size)
        total = self.store_repository.count()

        return StorePage(
            total=total,
            page=page,
            size=size,
            items=[self._to_response(store) for store in stores],
        )

    def create_store(self, store_data: StoreCreate) -> StoreResponse:
        """Create a new store with business validation"""
        self.logger.info(f"Creating store: {store_data.nom}")

        try:
            # Check if store name already exists
            existing_store = self.store_repository.get_by_name(store_data.nom)
            if existing_store:
                self.logger.warning(
                    f"Store creation failed - name already exists: {store_data.nom}"
                )
                raise ValueError(f"Store with name '{store_data.nom}' already exists")

            # Create the store
            store = self.store_repository.create(store_data)
            self.logger.info(f"Store created successfully with ID: {store.id}")

            log_business_operation(
                self.logger,
                operation="CREATE",
                entity="Store",
                entity_id=str(store.id),
                store_name=store_data.nom,
            )

            return self._to_response(store)
        except Exception as e:
            log_error_with_context(
                self.logger,
                e,
                {"operation": "create_store", "store_name": store_data.nom},
            )
            raise

    def update_store(
        self, store_id: int, store_data: StoreUpdate
    ) -> Optional[StoreResponse]:
        """Update an existing store with business validation"""
        # Check if store exists
        existing_store = self.store_repository.get_by_id(store_id)
        if not existing_store:
            return None

        # Check if new name conflicts with another store
        if store_data.nom and store_data.nom != existing_store.nom:
            name_conflict = self.store_repository.get_by_name(store_data.nom)
            if name_conflict and name_conflict.id != store_id:
                raise ValueError(f"Store with name '{store_data.nom}' already exists")

        # Update the store
        updated_store = self.store_repository.update(store_id, store_data)
        if updated_store:
            return self._to_response(updated_store)
        return None

    def delete_store(self, store_id: int) -> bool:
        """Delete a store"""
        # Additional business logic could go here
        # e.g., check if store has ongoing sales
        return self.store_repository.delete(store_id)

    def update_store_contact(
        self,
        store_id: int,
        email: Optional[str] = None,
        telephone: Optional[str] = None,
    ) -> Optional[StoreResponse]:
        """Update store contact information - Business operation"""
        store = self.store_repository.get_by_id(store_id)
        if not store:
            raise ValueError("Store not found")

        # Apply business logic using entity methods
        store.update_contact_info(telephone=telephone, email=email)

        # Update in repository
        update_data = StoreUpdate()
        if telephone:
            update_data.telephone = telephone
        if email:
            update_data.email = email

        updated_store = self.store_repository.update(store_id, update_data)
        if updated_store:
            return self._to_response(updated_store)
        return None

    def get_stores_with_contact(self) -> List[StoreResponse]:
        """Get stores with any contact information - Business query"""
        all_stores = self.store_repository.get_all(limit=1000)
        contact_stores = [
            store for store in all_stores if store.telephone or store.email
        ]
        return [self._to_response(store) for store in contact_stores]

    def get_stores_with_complete_contact(self) -> List[StoreResponse]:
        """Get stores with complete contact information - Business query"""
        all_stores = self.store_repository.get_all(limit=1000)
        complete_contact_stores = [
            store for store in all_stores if store.is_contact_complete()
        ]
        return [self._to_response(store) for store in complete_contact_stores]

    def _to_response(self, store: Store) -> StoreResponse:
        """Convert domain entity to response schema"""
        return StoreResponse(
            id=store.id,
            nom=store.nom,
            adresse=store.adresse,
            telephone=store.telephone,
            email=store.email,
        )
