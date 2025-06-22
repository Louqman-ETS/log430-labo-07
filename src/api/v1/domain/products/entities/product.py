from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class Product:
    """
    Product Entity - Core business object for the Products domain
    """

    id: Optional[int] = None
    code: str = ""
    nom: str = ""
    description: Optional[str] = None
    prix: Decimal = Decimal("0.00")
    quantite_stock: int = 0
    categorie_id: int = 0

    def __post_init__(self):
        if self.prix < 0:
            raise ValueError("Product price cannot be negative")
        if self.quantite_stock < 0:
            raise ValueError("Product stock quantity cannot be negative")
        if not self.code:
            raise ValueError("Product code is required")
        if not self.nom:
            raise ValueError("Product name is required")

    def is_in_stock(self) -> bool:
        """Check if product is available in stock"""
        return self.quantite_stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Reduce stock quantity (business logic)"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantite_stock < quantity:
            raise ValueError("Insufficient stock")
        self.quantite_stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Increase stock quantity (business logic)"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantite_stock += quantity

    def update_price(self, new_price: Decimal) -> None:
        """Update product price with validation"""
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        self.prix = new_price
