from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# Sale schemas
class SaleLineBase(BaseModel):
    quantite: int = Field(..., ge=1, description="Quantity")
    prix_unitaire: float = Field(..., gt=0, description="Unit price")
    product_id: int = Field(..., description="Product ID")

class SaleLineCreate(SaleLineBase):
    pass

class SaleLineResponse(SaleLineBase):
    id: int
    sale_id: int

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    montant_total: float = Field(default=0.0, description="Total amount")
    store_id: int = Field(..., description="Store ID")
    cash_register_id: int = Field(..., description="Cash register ID")

class SaleCreate(SaleBase):
    lines: List[SaleLineCreate] = []

class SaleUpdate(SaleBase):
    montant_total: Optional[float] = None
    store_id: Optional[int] = None
    cash_register_id: Optional[int] = None

class SaleResponse(SaleBase):
    id: int
    date_heure: datetime
    lines: List[SaleLineResponse] = []

    class Config:
        from_attributes = True

# Report schemas
class GlobalSummaryResponse(BaseModel):
    total_sales: int
    total_revenue: float
    total_products: int
    total_stores: int
    average_sale_amount: float

class StorePerformanceResponse(BaseModel):
    store_id: int
    store_name: Optional[str] = None
    sales_count: int
    revenue: float
    average_sale_amount: float
    performance_rating: str

class TopProductResponse(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    total_quantity_sold: int
    total_revenue: float
    sales_count: int

class SalesReportResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    store_id: Optional[int]
    total_sales: int
    total_revenue: float
    sales_data: List[dict]

# Stock schemas
class StoreStockBase(BaseModel):
    store_id: int = Field(..., description="Store ID")
    product_id: int = Field(..., description="Product ID")
    quantite_stock: int = Field(default=0, ge=0, description="Stock quantity")
    seuil_alerte: int = Field(default=20, ge=0, description="Alert threshold")

class StoreStockCreate(StoreStockBase):
    pass

class StoreStockUpdate(StoreStockBase):
    store_id: Optional[int] = None
    product_id: Optional[int] = None
    quantite_stock: Optional[int] = None
    seuil_alerte: Optional[int] = None

class StoreStockResponse(StoreStockBase):
    id: int

    class Config:
        from_attributes = True

class CentralStockBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantite_stock: int = Field(default=0, ge=0, description="Stock quantity")
    seuil_alerte: int = Field(default=20, ge=0, description="Alert threshold")

class CentralStockCreate(CentralStockBase):
    pass

class CentralStockUpdate(CentralStockBase):
    product_id: Optional[int] = None
    quantite_stock: Optional[int] = None
    seuil_alerte: Optional[int] = None

class CentralStockResponse(CentralStockBase):
    id: int

    class Config:
        from_attributes = True

# Restocking request schemas
class RestockingRequestBase(BaseModel):
    store_id: int = Field(..., description="Store ID")
    product_id: int = Field(..., description="Product ID")
    quantite_demandee: int = Field(..., ge=1, description="Requested quantity")
    statut: str = Field(default="en_attente", description="Status")

class RestockingRequestCreate(RestockingRequestBase):
    pass

class RestockingRequestUpdate(RestockingRequestBase):
    store_id: Optional[int] = None
    product_id: Optional[int] = None
    quantite_demandee: Optional[int] = None
    statut: Optional[str] = None

class RestockingRequestResponse(RestockingRequestBase):
    id: int
    date_demande: datetime

    class Config:
        from_attributes = True 