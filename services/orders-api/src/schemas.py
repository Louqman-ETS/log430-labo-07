from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum

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