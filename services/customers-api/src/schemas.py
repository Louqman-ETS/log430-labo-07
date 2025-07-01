from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AddressType(str, Enum):
    SHIPPING = "shipping"
    BILLING = "billing"

# Schémas pour les adresses
class AddressBase(BaseModel):
    type: AddressType
    title: Optional[str] = None
    street_address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="France", max_length=100)
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    type: Optional[AddressType] = None
    title: Optional[str] = None
    street_address: Optional[str] = Field(None, min_length=5, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=5, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: int
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schémas pour l'authentification
class CustomerLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class CustomerRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, and dashes')
        return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

# Schémas pour les clients
class CustomerBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None

class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=6, max_length=100)

class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None

class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerWithAddresses(CustomerResponse):
    addresses: List[AddressResponse] = []

# Schémas pour les tokens d'authentification
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    customer_id: Optional[int] = None

# Schémas pour les réponses d'authentification
class LoginResponse(BaseModel):
    customer: CustomerResponse
    token: Token

# Schémas pour les statistiques
class CustomerStats(BaseModel):
    total_customers: int
    active_customers: int
    new_customers_today: int
    customers_with_orders: int 