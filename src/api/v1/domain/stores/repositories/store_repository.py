from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from ..entities.store import Store
from ..schemas.store_schemas import StoreCreate, StoreUpdate


class StoreRepositoryInterface(ABC):
    """Abstract interface for Store Repository"""

    @abstractmethod
    def get_by_id(self, store_id: int) -> Optional[Store]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Store]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Store]:
        pass

    @abstractmethod
    def create(self, store_data: StoreCreate) -> Store:
        pass

    @abstractmethod
    def update(self, store_id: int, store_data: StoreUpdate) -> Optional[Store]:
        pass

    @abstractmethod
    def delete(self, store_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class StoreRepository(StoreRepositoryInterface):
    """Concrete implementation of Store Repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, store_id: int) -> Optional[Store]:
        from src.app.models.models import Magasin

        db_store = self.db.query(Magasin).filter(Magasin.id == store_id).first()
        if db_store:
            return self._to_entity(db_store)
        return None

    def get_by_name(self, name: str) -> Optional[Store]:
        from src.app.models.models import Magasin

        db_store = self.db.query(Magasin).filter(Magasin.nom == name).first()
        if db_store:
            return self._to_entity(db_store)
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Store]:
        from src.app.models.models import Magasin

        db_stores = self.db.query(Magasin).offset(skip).limit(limit).all()
        return [self._to_entity(db_store) for db_store in db_stores]

    def create(self, store_data: StoreCreate) -> Store:
        from src.app.models.models import Magasin

        db_store = Magasin(
            nom=store_data.nom,
            adresse=store_data.adresse,
            telephone=store_data.telephone,
            email=store_data.email,
        )
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        return self._to_entity(db_store)

    def update(self, store_id: int, store_data: StoreUpdate) -> Optional[Store]:
        from src.app.models.models import Magasin

        db_store = self.db.query(Magasin).filter(Magasin.id == store_id).first()
        if db_store:
            update_data = store_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_store, field, value)

            self.db.commit()
            self.db.refresh(db_store)
            return self._to_entity(db_store)
        return None

    def delete(self, store_id: int) -> bool:
        from src.app.models.models import Magasin

        db_store = self.db.query(Magasin).filter(Magasin.id == store_id).first()
        if db_store:
            self.db.delete(db_store)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        from src.app.models.models import Magasin

        return self.db.query(Magasin).count()

    def _to_entity(self, db_store) -> Store:
        """Convert SQLAlchemy model to domain entity"""
        # Handle potentially invalid email from database
        email = db_store.email
        if email and email.strip() and email.strip() != "string":
            # Clean the email and validate
            email = email.strip()
            # If email is invalid, set to None rather than raising error
            import re

            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(pattern, email):
                email = None
        else:
            email = None

        # Handle other fields that might have "string" as default value
        nom = db_store.nom if db_store.nom != "string" else "Nom non défini"
        adresse = db_store.adresse if db_store.adresse != "string" else None
        telephone = db_store.telephone if db_store.telephone != "string" else None

        return Store(
            id=db_store.id, nom=nom, adresse=adresse, telephone=telephone, email=email
        )
