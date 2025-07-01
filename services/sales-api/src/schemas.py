from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Schémas pour SaleLine
class SaleLineBase(BaseModel):
    product_id: int
    quantite: int = Field(gt=0, description="Quantité doit être positive")
    prix_unitaire: float = Field(gt=0, description="Prix unitaire doit être positif")

class SaleLineCreate(SaleLineBase):
    pass

class SaleLineResponse(SaleLineBase):
    id: int
    sale_id: int
    sous_total: float
    
    class Config:
        from_attributes = True

# Schémas pour Sale
class SaleBase(BaseModel):
    store_id: int
    cash_register_id: int
    notes: Optional[str] = None

class SaleCreate(SaleBase):
    sale_lines: List[SaleLineCreate] = Field(min_items=1, description="Au moins une ligne de vente requise")

class SaleResponse(SaleBase):
    id: int
    date_vente: datetime
    total: float
    sale_lines: List[SaleLineResponse] = []
    
    class Config:
        from_attributes = True

# Schéma pour les statistiques
class SalesStats(BaseModel):
    total_sales: int
    total_revenue: float
    average_sale_amount: float

# Schéma enrichi avec données des autres services
class SaleWithDetails(SaleResponse):
    store_name: Optional[str] = None
    cash_register_number: Optional[str] = None 