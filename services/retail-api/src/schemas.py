from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Store schemas
class StoreBase(BaseModel):
    nom: str = Field(..., description="Store name")
    adresse: Optional[str] = Field(None, description="Store address")
    telephone: Optional[str] = Field(None, description="Store phone number")
    email: Optional[str] = Field(None, description="Store email")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(StoreBase):
    nom: Optional[str] = None
    actif: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    actif: bool
    date_creation: datetime

    class Config:
        from_attributes = True


# Cash Register schemas
class CashRegisterBase(BaseModel):
    numero: int = Field(..., description="Cash register number within store")
    nom: str = Field(..., description="Cash register name")
    store_id: int = Field(..., description="Store ID")


class CashRegisterCreate(CashRegisterBase):
    pass


class CashRegisterUpdate(CashRegisterBase):
    numero: Optional[int] = None
    nom: Optional[str] = None
    store_id: Optional[int] = None
    actif: Optional[bool] = None


class CashRegisterResponse(CashRegisterBase):
    id: int
    actif: bool
    date_creation: datetime
    store: Optional[StoreResponse] = None

    class Config:
        from_attributes = True


# Sale Line schemas
class SaleLineBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantite: int = Field(..., gt=0, description="Quantity")
    prix_unitaire: float = Field(..., gt=0, description="Unit price")


class SaleLineCreate(SaleLineBase):
    pass


class SaleLineResponse(SaleLineBase):
    id: int
    sale_id: int
    sous_total: float

    class Config:
        from_attributes = True


# Sale schemas
class SaleBase(BaseModel):
    store_id: int = Field(..., description="Store ID")
    cash_register_id: int = Field(..., description="Cash register ID")
    notes: Optional[str] = Field(None, description="Sale notes")
    statut: str = Field(default="terminee", description="Sale status")


class SaleCreate(SaleBase):
    lines: List[SaleLineCreate] = Field(..., description="Sale lines")


class SaleUpdate(BaseModel):
    notes: Optional[str] = None
    statut: Optional[str] = None


class SaleResponse(SaleBase):
    id: int
    date_vente: datetime
    total: float
    store: Optional[StoreResponse] = None
    cash_register: Optional[CashRegisterResponse] = None
    sale_lines: List[SaleLineResponse] = []

    class Config:
        from_attributes = True


class SalePage(BaseModel):
    items: List[SaleResponse]
    total: int
    page: int
    size: int
    pages: int


# Store with details schemas
class StoreWithDetails(StoreResponse):
    cash_registers: List[CashRegisterResponse] = []
    total_sales: float = 0.0
    nombre_transactions: int = 0

    class Config:
        from_attributes = True


# Metrics schemas
class StoreMetricsBase(BaseModel):
    store_id: int = Field(..., description="Store ID")
    total_ventes: float = Field(default=0.0, description="Total sales")
    nombre_transactions: int = Field(default=0, description="Number of transactions")
    panier_moyen: float = Field(default=0.0, description="Average basket")


class StoreMetricsCreate(StoreMetricsBase):
    pass


class StoreMetricsResponse(StoreMetricsBase):
    id: int
    date_metrique: datetime
    store: Optional[StoreResponse] = None

    class Config:
        from_attributes = True


# Retail summary schemas
class RetailSummary(BaseModel):
    total_stores: int
    stores_actifs: int
    total_cash_registers: int
    cash_registers_actives: int
    total_sales: int
    total_revenue: float
    panier_moyen_global: float


class StorePerformance(BaseModel):
    store: StoreResponse
    total_ventes: float
    nombre_transactions: int
    panier_moyen: float
    derniere_vente: Optional[datetime] = None


# Sale creation with validation
class SaleCreateWithValidation(BaseModel):
    store_id: int = Field(..., description="Store ID")
    cash_register_id: int = Field(..., description="Cash register ID")
    lines: List[SaleLineCreate] = Field(..., min_items=1, description="Sale lines")
    notes: Optional[str] = Field(None, description="Sale notes")

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "cash_register_id": 1,
                "lines": [{"product_id": 1, "quantite": 2, "prix_unitaire": 10.50}],
                "notes": "Vente normale",
            }
        }
