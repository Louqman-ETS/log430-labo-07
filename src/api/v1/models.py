from pydantic import BaseModel
from typing import List, Optional


# Properties to receive on item creation
class ProductCreate(BaseModel):
    code: str
    nom: str
    description: Optional[str] = None
    prix: float
    quantite_stock: Optional[int] = 0
    categorie_id: int


# Properties to receive on item update
class ProductUpdate(BaseModel):
    code: Optional[str] = None
    nom: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    quantite_stock: Optional[int] = None
    categorie_id: Optional[int] = None


# Properties shared by models stored in DB
class ProductInDBBase(BaseModel):
    id: int
    code: str
    nom: str
    description: Optional[str] = None
    prix: float
    quantite_stock: int
    categorie_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Product(ProductInDBBase):
    pass


# Properties stored in DB
class ProductInDB(ProductInDBBase):
    pass


class ProductPage(BaseModel):
    total: int
    page: int
    size: int
    items: List[Product]


# Store Schemas
class StoreBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class StoreInDBBase(StoreBase):
    id: int

    class Config:
        orm_mode = True


class Store(StoreInDBBase):
    pass


class StoreInDB(StoreInDBBase):
    pass


class StorePage(BaseModel):
    total: int
    page: int
    size: int
    items: List[Store]


# Report Schemas
class GlobalSummary(BaseModel):
    total_revenue: float
    total_sales_count: int
    average_ticket: float


class StorePerformance(BaseModel):
    store_id: int
    store_name: str
    sales_count: int
    revenue: float
    average_ticket: float


class TopProduct(BaseModel):
    product_code: str
    product_name: str
    total_quantity_sold: int
    total_revenue: float
    total_orders: int
