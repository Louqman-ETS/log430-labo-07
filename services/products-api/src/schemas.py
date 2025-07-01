from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

# Category schemas
class CategoryBase(BaseModel):
    nom: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    nom: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    code: str = Field(..., description="Product code")
    nom: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    prix: float = Field(..., gt=0, description="Product price")
    quantite_stock: int = Field(default=0, ge=0, description="Stock quantity")
    categorie_id: int = Field(..., description="Category ID")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    code: Optional[str] = None
    nom: Optional[str] = None
    prix: Optional[float] = None
    quantite_stock: Optional[int] = None
    categorie_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

class ProductPage(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int 