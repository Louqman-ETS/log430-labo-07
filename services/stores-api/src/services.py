from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import math
import re

from .models import Store, CashRegister
from .schemas import StoreCreate, StoreUpdate, CashRegisterCreate, CashRegisterUpdate


class StoreService:
    def __init__(self, db: Session):
        self.db = db

    def get_store(self, store_id: int) -> Optional[Store]:
        return self.db.query(Store).filter(Store.id == store_id).first()

    def get_store_by_name(self, name: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.nom == name).first()

    def get_stores_paginated(self, page: int = 1, size: int = 20, search: Optional[str] = None):
        query = self.db.query(Store)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Store.nom.ilike(f"%{search}%"),
                    Store.adresse.ilike(f"%{search}%"),
                    Store.email.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        stores = query.offset(offset).limit(size).all()
        
        # Calculate pages
        pages = math.ceil(total / size) if total > 0 else 1
        
        return {
            "items": stores,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    def get_stores(self) -> List[Store]:
        return self.db.query(Store).all()

    def create_store(self, store: StoreCreate) -> Store:
        # Check if store name already exists
        existing = self.db.query(Store).filter(Store.nom == store.nom).first()
        if existing:
            raise ValueError(f"Store with name '{store.nom}' already exists")
        
        # Validate email if provided
        if store.email and not self._is_valid_email(store.email):
            raise ValueError("Invalid email format")
        
        db_store = Store(**store.dict())
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        return db_store

    def update_store(self, store_id: int, store: StoreUpdate) -> Optional[Store]:
        db_store = self.get_store(store_id)
        if not db_store:
            return None
        
        # Check for duplicate name if updating name
        if store.nom and store.nom != db_store.nom:
            existing = self.db.query(Store).filter(Store.nom == store.nom).first()
            if existing:
                raise ValueError(f"Store with name '{store.nom}' already exists")
        
        # Validate email if updating email
        if store.email and not self._is_valid_email(store.email):
            raise ValueError("Invalid email format")
        
        update_data = store.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_store, field, value)
        
        self.db.commit()
        self.db.refresh(db_store)
        return db_store

    def delete_store(self, store_id: int) -> bool:
        db_store = self.get_store(store_id)
        if not db_store:
            return False
        
        # Check if store has cash registers
        registers_count = self.db.query(CashRegister).filter(CashRegister.store_id == store_id).count()
        if registers_count > 0:
            raise ValueError(f"Cannot delete store with {registers_count} cash registers")
        
        self.db.delete(db_store)
        self.db.commit()
        return True

    def update_store_contact(self, store_id: int, email: Optional[str] = None, telephone: Optional[str] = None) -> Optional[Store]:
        db_store = self.get_store(store_id)
        if not db_store:
            return None
        
        if email:
            if not self._is_valid_email(email):
                raise ValueError("Invalid email format")
            db_store.email = email
        
        if telephone:
            db_store.telephone = telephone
        
        self.db.commit()
        self.db.refresh(db_store)
        return db_store

    def get_stores_with_contact(self) -> List[Store]:
        return self.db.query(Store).filter(
            (Store.email.isnot(None)) | (Store.telephone.isnot(None))
        ).all()

    def get_stores_with_complete_contact(self) -> List[Store]:
        return self.db.query(Store).filter(
            Store.email.isnot(None),
            Store.telephone.isnot(None),
            Store.adresse.isnot(None)
        ).all()

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation"""
        if not email or not email.strip():
            return False
        # Basic email pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))


class CashRegisterService:
    def __init__(self, db: Session):
        self.db = db

    def get_cash_register(self, register_id: int) -> Optional[CashRegister]:
        return self.db.query(CashRegister).filter(CashRegister.id == register_id).first()

    def get_cash_registers_by_store(self, store_id: int) -> List[CashRegister]:
        return self.db.query(CashRegister).filter(CashRegister.store_id == store_id).all()

    def get_all_cash_registers(self) -> List[CashRegister]:
        return self.db.query(CashRegister).all()

    def create_cash_register(self, register: CashRegisterCreate) -> CashRegister:
        # Check if store exists
        store = self.db.query(Store).filter(Store.id == register.store_id).first()
        if not store:
            raise ValueError(f"Store with id {register.store_id} not found")
        
        # Check if register number already exists for this store
        existing = self.db.query(CashRegister).filter(
            CashRegister.store_id == register.store_id,
            CashRegister.numero == register.numero
        ).first()
        if existing:
            raise ValueError(f"Cash register number {register.numero} already exists for store {register.store_id}")
        
        db_register = CashRegister(**register.dict())
        self.db.add(db_register)
        self.db.commit()
        self.db.refresh(db_register)
        return db_register

    def update_cash_register(self, register_id: int, register: CashRegisterUpdate) -> Optional[CashRegister]:
        db_register = self.get_cash_register(register_id)
        if not db_register:
            return None
        
        # Check for duplicate number if updating
        if register.numero and register.store_id and (
            register.numero != db_register.numero or register.store_id != db_register.store_id
        ):
            existing = self.db.query(CashRegister).filter(
                CashRegister.store_id == register.store_id,
                CashRegister.numero == register.numero,
                CashRegister.id != register_id
            ).first()
            if existing:
                raise ValueError(f"Cash register number {register.numero} already exists for store {register.store_id}")
        
        # Check if store exists if updating store
        if register.store_id and register.store_id != db_register.store_id:
            store = self.db.query(Store).filter(Store.id == register.store_id).first()
            if not store:
                raise ValueError(f"Store with id {register.store_id} not found")
        
        update_data = register.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_register, field, value)
        
        self.db.commit()
        self.db.refresh(db_register)
        return db_register

    def delete_cash_register(self, register_id: int) -> bool:
        db_register = self.get_cash_register(register_id)
        if not db_register:
            return False
        
        self.db.delete(db_register)
        self.db.commit()
        return True 