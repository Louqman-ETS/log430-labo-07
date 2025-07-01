from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# CashRegister schemas
class CashRegisterBase(BaseModel):
    numero: int = Field(..., ge=1, description="Cash register number")
    nom: str = Field(..., description="Cash register name")
    store_id: int = Field(..., description="Store ID")

class CashRegisterCreate(CashRegisterBase):
    pass

class CashRegisterUpdate(CashRegisterBase):
    numero: Optional[int] = None
    nom: Optional[str] = None
    store_id: Optional[int] = None

class CashRegisterResponse(CashRegisterBase):
    id: int

    class Config:
        from_attributes = True

# Store schemas
class StoreBase(BaseModel):
    nom: str = Field(..., description="Store name")
    adresse: Optional[str] = Field(None, description="Store address")
    telephone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")

class StoreCreate(StoreBase):
    pass

class StoreUpdate(StoreBase):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

class StoreResponse(StoreBase):
    id: int
    cash_registers: Optional[List[CashRegisterResponse]] = []

    class Config:
        from_attributes = True

class StorePage(BaseModel):
    items: List[StoreResponse]
    total: int
    page: int
    size: int
    pages: int 