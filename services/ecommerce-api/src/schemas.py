from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class AddressType(str, Enum):
    SHIPPING = "shipping"
    BILLING = "billing"


# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================


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

    @validator("phone")
    def validate_phone(cls, v):
        if v and not v.replace("+", "").replace(" ", "").replace("-", "").isdigit():
            raise ValueError(
                "Phone number must contain only digits, spaces, and dashes"
            )
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


# ============================================================================
# CART SCHEMAS
# ============================================================================


# Schémas pour les éléments de panier
class CartItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, le=100)


class ProductInfo(BaseModel):
    """Informations produit récupérées depuis l'API Products"""

    id: int
    nom: str
    prix: Decimal
    description: Optional[str] = None
    categorie_nom: Optional[str] = None
    stock_disponible: Optional[int] = None


class CartItemResponse(CartItemBase):
    id: int
    cart_id: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime

    # Informations produit enrichies
    product_info: Optional[ProductInfo] = None

    class Config:
        from_attributes = True


class CartItemWithProduct(CartItemResponse):
    """CartItem avec informations produit complètes"""

    pass


# Schémas pour les paniers
class CartBase(BaseModel):
    customer_id: Optional[int] = None
    session_id: Optional[str] = None


class CartCreate(CartBase):
    pass


class CartResponse(CartBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    # Propriétés calculées
    total_items: int = 0
    total_price: Decimal = Decimal("0.00")

    # Relations
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True


class CartWithProducts(CartResponse):
    """Panier avec informations produits complètes"""

    items: List[CartItemWithProduct] = []


# Schémas pour les opérations sur le panier
class AddToCartRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0, le=100)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., gt=0, le=100)


class CartSummary(BaseModel):
    """Résumé du panier"""

    cart_id: int
    total_items: int
    total_price: Decimal
    items_count: int
    last_updated: datetime


# Schémas pour la synchronisation avec d'autres services
class StockCheckRequest(BaseModel):
    product_id: int
    requested_quantity: int


class StockCheckResponse(BaseModel):
    product_id: int
    available_stock: int
    is_available: bool


class CartValidationResponse(BaseModel):
    """Réponse de validation du panier"""

    is_valid: bool
    total_price: Decimal
    issues: List[str] = []
    unavailable_items: List[int] = []  # IDs des produits non disponibles


# Schémas pour les statistiques
class CartStats(BaseModel):
    total_active_carts: int
    total_items_in_carts: int
    average_cart_value: Decimal
    abandoned_carts_today: int


# ============================================================================
# ORDER SCHEMAS
# ============================================================================


# Schémas pour les éléments de commande
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


# Schémas pour les commandes
class CheckoutRequest(BaseModel):
    """Requête de checkout depuis un panier"""

    cart_id: int
    customer_id: int
    shipping_address: str = Field(..., min_length=10)
    billing_address: str = Field(..., min_length=10)
    payment_method: str = Field(default="card")


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    cart_id: Optional[int]
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    shipping_address: str
    billing_address: str
    total_items: int
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None

    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class PaymentUpdateStatus(BaseModel):
    payment_status: PaymentStatus


# Schémas pour les statistiques
class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_revenue: Decimal
    orders_today: int
