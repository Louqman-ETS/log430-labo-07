from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import time
import uuid

from src.database import get_db
from src.services import CartService, ProductService, ExternalServiceError
import src.schemas as schemas
import src.models as models

logger = logging.getLogger(__name__)
router = APIRouter()


def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(db)


# =========================================================================
# ROUTES STATIQUES EN PREMIER
# =========================================================================


@router.get("/", response_model=List[schemas.CartResponse])
def get_carts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    session_id: Optional[str] = Query(None),
    service: CartService = Depends(get_cart_service),
):
    """Récupérer tous les paniers avec filtres optionnels"""
    return service.get_carts(
        skip=skip, limit=limit, customer_id=customer_id, session_id=session_id
    )


@router.get("/stats/summary", response_model=schemas.CartStats)
def get_cart_statistics(service: CartService = Depends(get_cart_service)):
    """Récupérer les statistiques des paniers"""
    return service.get_cart_stats()


@router.get("/customer/{customer_id}", response_model=List[schemas.CartResponse])
def get_customer_carts(
    customer_id: int, service: CartService = Depends(get_cart_service)
):
    """Récupérer tous les paniers d'un client"""
    return service.get_customer_carts(customer_id)


@router.get("/session/{session_id}", response_model=schemas.CartResponse)
def get_cart_by_session(
    session_id: str, service: CartService = Depends(get_cart_service)
):
    """Récupérer un panier par session ID"""
    cart = service.get_cart_by_session(session_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


# =========================================================================
# ENDPOINTS ITEMS ET VALIDATION
# =========================================================================


@router.get("/{cart_id}/with-products", response_model=schemas.CartWithProducts)
def get_cart_with_products(
    cart_id: int, service: CartService = Depends(get_cart_service)
):
    """Récupérer un panier avec les informations produits complètes"""
    cart = service.get_cart_with_products(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.get("/{cart_id}/items", response_model=List[schemas.CartItemResponse])
def get_cart_items(cart_id: int, service: CartService = Depends(get_cart_service)):
    """Récupérer tous les éléments d'un panier"""
    return service.get_cart_items(cart_id)


@router.post(
    "/{cart_id}/items",
    response_model=schemas.CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    cart_id: int,
    item: schemas.AddToCartRequest,
    service: CartService = Depends(get_cart_service),
):
    """Ajouter un élément au panier"""
    try:
        return await service.add_item_to_cart(cart_id, item)
    except Exception as e:
        logger.error(f"Error adding item to cart: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cart_id}/items/{item_id}", response_model=schemas.CartItemResponse)
def update_cart_item(
    cart_id: int,
    item_id: int,
    item: schemas.UpdateCartItemRequest,
    service: CartService = Depends(get_cart_service),
):
    """Mettre à jour un élément du panier"""
    try:
        updated_item = service.update_cart_item(cart_id, item_id, item)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}/items/{item_id}", response_model=schemas.CartItemResponse)
def remove_cart_item(
    cart_id: int, item_id: int, service: CartService = Depends(get_cart_service)
):
    """Supprimer un élément du panier"""
    item = service.get_cart_item(cart_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    try:
        deleted = service.remove_cart_item(cart_id, item_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}/items", response_model=schemas.CartResponse)
def clear_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    """Vider un panier"""
    cart = service.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    try:
        cleared_cart = service.clear_cart(cart_id)
        if not cleared_cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cleared_cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/validate", response_model=schemas.CartValidationResponse)
async def validate_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    """Valider un panier (vérifier stock, prix, etc.)"""
    try:
        return await service.validate_cart(cart_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/check-stock", response_model=List[schemas.StockCheckResponse])
async def check_cart_stock(
    cart_id: int, service: CartService = Depends(get_cart_service)
):
    """Vérifier le stock pour tous les éléments d'un panier"""
    try:
        return await service.check_cart_stock(cart_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================================
# ENDPOINTS DYNAMIQUES A LA FIN
# =========================================================================


@router.post(
    "/", response_model=schemas.CartResponse, status_code=status.HTTP_201_CREATED
)
def create_cart(
    cart: schemas.CartCreate, service: CartService = Depends(get_cart_service)
):
    """Créer un nouveau panier"""
    try:
        return service.create_cart(cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cart_id}", response_model=schemas.CartResponse)
def update_cart(
    cart_id: int,
    cart: schemas.CartCreate,
    service: CartService = Depends(get_cart_service),
):
    """Mettre à jour un panier"""
    try:
        updated_cart = service.update_cart(cart_id, cart)
        if not updated_cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return updated_cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}", response_model=schemas.CartResponse)
def delete_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    """Supprimer un panier"""
    cart = service.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    try:
        deleted = service.delete_cart(cart_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{cart_id}", response_model=schemas.CartResponse)
def get_cart(cart_id: int, service: CartService = Depends(get_cart_service)):
    """Récupérer un panier par ID"""
    cart = service.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart
