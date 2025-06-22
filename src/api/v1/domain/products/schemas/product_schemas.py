from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    """Schema for creating a new product"""

    code: str = Field(..., min_length=1, description="Product code")
    nom: str = Field(..., min_length=1, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    prix: Decimal = Field(..., ge=0, description="Product price")
    quantite_stock: int = Field(0, ge=0, description="Stock quantity")
    categorie_id: int = Field(..., gt=0, description="Category ID")


class ProductUpdate(BaseModel):
    """Schema for updating an existing product"""

    code: Optional[str] = Field(None, min_length=1, description="Product code")
    nom: Optional[str] = Field(None, min_length=1, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    prix: Optional[Decimal] = Field(None, ge=0, description="Product price")
    quantite_stock: Optional[int] = Field(None, ge=0, description="Stock quantity")
    categorie_id: Optional[int] = Field(None, gt=0, description="Category ID")


class ProductResponse(BaseModel):
    """Schema for product response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str
    description: Optional[str] = None
    prix: Decimal
    quantite_stock: int
    categorie_id: int


class ProductPage(BaseModel):
    """Schema for paginated product response"""

    total: int
    page: int
    size: int
    items: List[ProductResponse]
