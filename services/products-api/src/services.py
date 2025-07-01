from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import math

from .models import Product, Category
from .schemas import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_category(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_categories(self) -> List[Category]:
        return self.db.query(Category).all()

    def create_category(self, category: CategoryCreate) -> Category:
        # Check if category already exists
        existing = self.db.query(Category).filter(Category.nom == category.nom).first()
        if existing:
            raise ValueError(f"Category with name '{category.nom}' already exists")
        
        db_category = Category(**category.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update_category(self, category_id: int, category: CategoryUpdate) -> Optional[Category]:
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        # Check for duplicate name if updating name
        if category.nom and category.nom != db_category.nom:
            existing = self.db.query(Category).filter(Category.nom == category.nom).first()
            if existing:
                raise ValueError(f"Category with name '{category.nom}' already exists")
        
        update_data = category.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: int) -> bool:
        db_category = self.get_category(category_id)
        if not db_category:
            return False
        
        # Check if category has products
        products_count = self.db.query(Product).filter(Product.categorie_id == category_id).count()
        if products_count > 0:
            raise ValueError(f"Cannot delete category with {products_count} products")
        
        self.db.delete(db_category)
        self.db.commit()
        return True


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_code(self, code: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.code == code).first()

    def get_products_paginated(self, page: int = 1, size: int = 20, search: Optional[str] = None):
        query = self.db.query(Product)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Product.nom.ilike(f"%{search}%"),
                    Product.code.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        products = query.offset(offset).limit(size).all()
        
        # Calculate pages
        pages = math.ceil(total / size) if total > 0 else 1
        
        return {
            "items": products,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    def create_product(self, product: ProductCreate) -> Product:
        # Check if product code already exists
        existing = self.db.query(Product).filter(Product.code == product.code).first()
        if existing:
            raise ValueError(f"Product with code '{product.code}' already exists")
        
        # Check if category exists
        category = self.db.query(Category).filter(Category.id == product.categorie_id).first()
        if not category:
            raise ValueError(f"Category with id {product.categorie_id} not found")
        
        db_product = Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update_product(self, product_id: int, product: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        # Check for duplicate code if updating code
        if product.code and product.code != db_product.code:
            existing = self.db.query(Product).filter(Product.code == product.code).first()
            if existing:
                raise ValueError(f"Product with code '{product.code}' already exists")
        
        # Check if category exists if updating category
        if product.categorie_id and product.categorie_id != db_product.categorie_id:
            category = self.db.query(Category).filter(Category.id == product.categorie_id).first()
            if not category:
                raise ValueError(f"Category with id {product.categorie_id} not found")
        
        update_data = product.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        db_product = self.get_product(product_id)
        if not db_product:
            return False
        
        self.db.delete(db_product)
        self.db.commit()
        return True

    def reduce_product_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        if db_product.quantite_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {db_product.quantite_stock}, Requested: {quantity}")
        
        db_product.quantite_stock -= quantity
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        return self.db.query(Product).filter(Product.quantite_stock <= threshold).all() 