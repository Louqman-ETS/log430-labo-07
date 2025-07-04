from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import time
import uuid

from src.database import get_db
import src.schemas as schemas
import src.models as models
from src.services import OrderService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


# ============================================================================
# ORDER ENDPOINTS
# ============================================================================


@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    status: Optional[schemas.OrderStatus] = Query(None),
    service: OrderService = Depends(get_order_service),
):
    """Récupérer toutes les commandes avec filtres optionnels"""
    return service.get_orders(
        skip=skip, limit=limit, customer_id=customer_id, status=status
    )


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    """Récupérer une commande par ID"""
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post(
    "/checkout",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def checkout_cart(
    checkout_data: schemas.CheckoutRequest,
    service: OrderService = Depends(get_order_service),
):
    """Traiter une commande de checkout depuis un panier"""
    try:
        return await service.process_checkout(checkout_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdateStatus,
    service: OrderService = Depends(get_order_service),
):
    """Mettre à jour le statut d'une commande"""
    try:
        updated_order = service.update_order_status(order_id, status_update.status)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/payment-status", response_model=schemas.OrderResponse)
def update_payment_status(
    order_id: int,
    payment_update: schemas.PaymentUpdateStatus,
    service: OrderService = Depends(get_order_service),
):
    """Mettre à jour le statut de paiement d'une commande"""
    try:
        updated_order = service.update_payment_status(
            order_id, payment_update.payment_status
        )
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}", response_model=List[schemas.OrderResponse])
def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: OrderService = Depends(get_order_service),
):
    """Récupérer toutes les commandes d'un client"""
    return service.get_customer_orders(customer_id, skip=skip, limit=limit)


@router.get("/stats/summary", response_model=schemas.OrderStats)
def get_order_statistics(service: OrderService = Depends(get_order_service)):
    """Récupérer les statistiques des commandes"""
    return service.get_order_stats()


# ============================================================================
# ORDER ITEM ENDPOINTS
# ============================================================================


@router.get("/{order_id}/items", response_model=List[schemas.OrderItemResponse])
def get_order_items(order_id: int, service: OrderService = Depends(get_order_service)):
    """Récupérer tous les éléments d'une commande"""
    return service.get_order_items(order_id)


# ============================================================================
# ORDER TRACKING ENDPOINTS
# ============================================================================


@router.get("/{order_id}/tracking")
def get_order_tracking(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    """Récupérer les informations de suivi d'une commande"""
    tracking = service.get_order_tracking(order_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Order not found")
    return tracking


@router.post("/{order_id}/confirm")
def confirm_order(order_id: int, service: OrderService = Depends(get_order_service)):
    """Confirmer une commande"""
    try:
        confirmed_order = service.confirm_order(order_id)
        if not confirmed_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order confirmed successfully", "order_id": order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/ship")
def ship_order(
    order_id: int,
    tracking_number: Optional[str] = None,
    service: OrderService = Depends(get_order_service),
):
    """Marquer une commande comme expédiée"""
    try:
        shipped_order = service.ship_order(order_id, tracking_number)
        if not shipped_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order shipped successfully", "order_id": order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/deliver")
def deliver_order(order_id: int, service: OrderService = Depends(get_order_service)):
    """Marquer une commande comme livrée"""
    try:
        delivered_order = service.deliver_order(order_id)
        if not delivered_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order delivered successfully", "order_id": order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    service: OrderService = Depends(get_order_service),
):
    """Annuler une commande"""
    try:
        cancelled_order = service.cancel_order(order_id, reason)
        if not cancelled_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order cancelled successfully", "order_id": order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
