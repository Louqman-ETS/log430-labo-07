from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Category schemas
class CategoryBase(BaseModel):
    nom: str = Field(..., min_length=1, description="Category name")
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
    seuil_alerte: int = Field(default=10, ge=0, description="Stock alert threshold")
    categorie_id: int = Field(..., description="Category ID")
    actif: bool = Field(default=True, description="Product active status")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    code: Optional[str] = None
    nom: Optional[str] = None
    prix: Optional[float] = None
    quantite_stock: Optional[int] = None
    seuil_alerte: Optional[int] = None
    categorie_id: Optional[int] = None
    actif: Optional[bool] = None


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


# Stock Movement schemas
class StockMovementBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    type_mouvement: str = Field(
        ..., description="Movement type: entree, sortie, ajustement"
    )
    quantite: int = Field(..., description="Quantity moved")
    raison: Optional[str] = Field(None, description="Reason for movement")
    reference: Optional[str] = Field(None, description="External reference")
    utilisateur: Optional[str] = Field(None, description="User who made the movement")


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementResponse(StockMovementBase):
    id: int
    date_mouvement: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# Stock Alert schemas
class StockAlertBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    type_alerte: str = Field(
        ..., description="Alert type: stock_faible, rupture, surstock"
    )
    message: str = Field(..., description="Alert message")


class StockAlertCreate(StockAlertBase):
    pass


class StockAlertUpdate(BaseModel):
    resolu: bool = Field(..., description="Alert resolved status")


class StockAlertResponse(StockAlertBase):
    id: int
    date_creation: datetime
    resolu: bool
    date_resolution: Optional[datetime] = None
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# Stock Management schemas
class StockAdjustment(BaseModel):
    quantite: int = Field(
        ...,
        description="Quantity to adjust (positive for increase, negative for decrease)",
    )
    raison: str = Field(..., description="Reason for adjustment")
    reference: Optional[str] = Field(None, description="External reference")
    utilisateur: Optional[str] = Field(None, description="User making the adjustment")


class StockInfo(BaseModel):
    product_id: int
    quantite_stock: int
    seuil_alerte: int
    status: str  # "normal", "faible", "rupture", "surstock"
    dernier_mouvement: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory schemas
class InventorySummary(BaseModel):
    total_products: int
    produits_en_stock: int
    produits_rupture: int
    produits_faible_stock: int
    valeur_totale: float
    alertes_actives: int


class ProductStockStatus(BaseModel):
    product: ProductResponse
    stock_info: StockInfo
    derniers_mouvements: List[StockMovementResponse] = []
