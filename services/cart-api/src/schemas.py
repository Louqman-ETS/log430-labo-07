from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

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
    total_price: Decimal = Decimal('0.00')
    
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