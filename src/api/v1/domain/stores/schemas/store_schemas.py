from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class StoreCreate(BaseModel):
    """Schema for creating a new store"""

    nom: str = Field(..., min_length=1, description="Store name")
    adresse: Optional[str] = Field(None, description="Store address")
    telephone: Optional[str] = Field(None, description="Store phone number")
    email: Optional[str] = Field(None, description="Store email")


class StoreUpdate(BaseModel):
    """Schema for updating an existing store"""

    nom: Optional[str] = Field(None, min_length=1, description="Store name")
    adresse: Optional[str] = Field(None, description="Store address")
    telephone: Optional[str] = Field(None, description="Store phone number")
    email: Optional[str] = Field(None, description="Store email")


class StoreResponse(BaseModel):
    """Schema for store response"""

    id: int
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True


class StorePage(BaseModel):
    """Schema for paginated store response"""

    total: int
    page: int
    size: int
    items: List[StoreResponse]
