from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Réutiliser les enums du modèle
from src.models import SagaState, SagaStep, SagaStepStatus


# ============================================================================
# SCHEMAS DE REQUÊTE
# ============================================================================

class OrderProcessingSagaRequest(BaseModel):
    """Requête pour déclencher une saga de traitement de commande"""
    customer_id: int = Field(..., description="ID du client")
    cart_id: Optional[int] = Field(None, description="ID du panier (optionnel)")
    products: List[Dict[str, Any]] = Field(..., description="Liste des produits à commander")
    shipping_address: str = Field(..., description="Adresse de livraison")
    billing_address: str = Field(..., description="Adresse de facturation")
    payment_method: str = Field(default="credit_card", description="Méthode de paiement")
    simulate_failure: Optional[str] = Field(None, description="Simuler un échec à une étape (stock/payment)")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "cart_id": 123,
                "products": [
                    {"product_id": 1, "quantity": 2, "price": 29.99},
                    {"product_id": 2, "quantity": 1, "price": 59.99}
                ],
                "shipping_address": "123 Main St, City, State, ZIP",
                "billing_address": "123 Main St, City, State, ZIP",
                "payment_method": "credit_card",
                "simulate_failure": None
            }
        }


class CustomerOrderProcessingSagaRequest(BaseModel):
    """Requête pour déclencher une saga de traitement de commande pour un client spécifique (customer_id dans l'URL)"""
    cart_id: Optional[int] = Field(None, description="ID du panier (optionnel)")
    products: List[Dict[str, Any]] = Field(..., description="Liste des produits à commander")
    shipping_address: str = Field(..., description="Adresse de livraison")
    billing_address: str = Field(..., description="Adresse de facturation")
    payment_method: str = Field(default="credit_card", description="Méthode de paiement")
    simulate_failure: Optional[str] = Field(None, description="Simuler un échec à une étape (stock/payment)")

    class Config:
        json_schema_extra = {
            "example": {
                "cart_id": 123,
                "products": [
                    {"product_id": 1, "quantity": 2, "price": 29.99},
                    {"product_id": 2, "quantity": 1, "price": 59.99}
                ],
                "shipping_address": "123 Main St, City, State, ZIP",
                "billing_address": "123 Main St, City, State, ZIP",
                "payment_method": "credit_card",
                "simulate_failure": None
            }
        }


class SagaStatusRequest(BaseModel):
    """Requête pour obtenir le statut d'une saga"""
    saga_id: str = Field(..., description="ID unique de la saga")


# ============================================================================
# SCHEMAS DE RÉPONSE
# ============================================================================

class SagaStepExecutionResponse(BaseModel):
    """Réponse pour l'exécution d'une étape"""
    step: SagaStep
    step_order: int
    status: SagaStepStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    compensation_step: Optional[SagaStep] = None

    class Config:
        from_attributes = True


class SagaResponse(BaseModel):
    """Réponse pour une saga"""
    saga_id: str
    saga_type: str
    state: SagaState
    payload: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    steps: List[SagaStepExecutionResponse] = []

    class Config:
        from_attributes = True


class SagaEventResponse(BaseModel):
    """Réponse pour un événement de saga"""
    saga_id: str
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SagaStatsResponse(BaseModel):
    """Statistiques des sagas"""
    total_sagas: int
    pending_sagas: int
    completed_sagas: int
    failed_sagas: int
    compensated_sagas: int
    average_duration_ms: Optional[float] = None
    success_rate: float
    total_steps_executed: int
    total_compensations: int


class SagaListResponse(BaseModel):
    """Liste paginée de sagas"""
    items: List[SagaResponse]
    total: int
    page: int
    size: int
    pages: int


# ============================================================================
# SCHEMAS SPÉCIALISÉS
# ============================================================================

class StockCheckResponse(BaseModel):
    """Réponse de vérification de stock"""
    product_id: int
    available_quantity: int
    requested_quantity: int
    sufficient: bool
    
    
class StockReservationResponse(BaseModel):
    """Réponse de réservation de stock"""
    product_id: int
    reserved_quantity: int
    new_stock_level: int
    reservation_id: Optional[str] = None


class OrderCreationResponse(BaseModel):
    """Réponse de création de commande"""
    order_id: int
    order_number: str
    total_amount: float
    status: str


class PaymentProcessingResponse(BaseModel):
    """Réponse de traitement de paiement"""
    payment_id: str
    amount: float
    status: str
    transaction_id: Optional[str] = None 