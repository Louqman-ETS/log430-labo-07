from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from ..entities.product import Product
from ..schemas.product_schemas import ProductCreate, ProductUpdate


class ProductRepositoryInterface(ABC):
    """Abstract interface for Product Repository"""

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Product]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        pass

    @abstractmethod
    def create(self, product_data: ProductCreate) -> Product:
        pass

    @abstractmethod
    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class ProductRepository(ProductRepositoryInterface):
    """Concrete implementation of Product Repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        from src.app.models.models import Produit

        db_product = self.db.query(Produit).filter(Produit.id == product_id).first()
        if db_product:
            return self._to_entity(db_product)
        return None

    def get_by_code(self, code: str) -> Optional[Product]:
        from src.app.models.models import Produit

        db_product = self.db.query(Produit).filter(Produit.code == code).first()
        if db_product:
            return self._to_entity(db_product)
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        from src.app.models.models import Produit

        db_products = self.db.query(Produit).offset(skip).limit(limit).all()
        return [self._to_entity(db_product) for db_product in db_products]

    def create(self, product_data: ProductCreate) -> Product:
        from src.app.models.models import Produit

        db_product = Produit(
            code=product_data.code,
            nom=product_data.nom,
            description=product_data.description,
            prix=float(product_data.prix),
            quantite_stock=product_data.quantite_stock,
            categorie_id=product_data.categorie_id,
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return self._to_entity(db_product)

    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        from src.app.models.models import Produit

        db_product = self.db.query(Produit).filter(Produit.id == product_id).first()
        if db_product:
            update_data = product_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "prix" and value is not None:
                    value = float(value)
                setattr(db_product, field, value)

            self.db.commit()
            self.db.refresh(db_product)
            return self._to_entity(db_product)
        return None

    def delete(self, product_id: int) -> bool:
        from src.app.models.models import Produit

        db_product = self.db.query(Produit).filter(Produit.id == product_id).first()
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        from src.app.models.models import Produit

        return self.db.query(Produit).count()

    def _to_entity(self, db_product) -> Product:
        """Convert SQLAlchemy model to domain entity"""
        return Product(
            id=db_product.id,
            code=db_product.code,
            nom=db_product.nom,
            description=db_product.description,
            prix=db_product.prix,
            quantite_stock=db_product.quantite_stock,
            categorie_id=db_product.categorie_id,
        )
