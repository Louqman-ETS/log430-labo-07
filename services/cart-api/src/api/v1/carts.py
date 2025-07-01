from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from ...database import get_db
from ...services import CartService, CartItemService, CartStatsService, ProductService, ExternalServiceError
from ... import schemas

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(
    cart_data: schemas.CartCreate,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🛒 Créer un nouveau panier"""
    logger.info(f"🛒 Création panier pour client: {cart_data.customer_id} / session: {cart_data.session_id} [Request-ID: {x_request_id}]")
    
    try:
        cart = CartService.create_cart(db, cart_data)
        logger.info(f"✅ Panier créé (ID: {cart.id}) [Request-ID: {x_request_id}]")
        
        response = schemas.CartResponse.from_orm(cart)
        response.total_items = cart.total_items
        response.total_price = cart.total_price
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur création panier: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Cart creation failed",
                "message": "Erreur lors de la création du panier",
                "service": "cart-api"
            }
        )

@router.get("/customer/{customer_id}", response_model=schemas.CartResponse)
def get_customer_cart(
    customer_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Récupérer le panier d'un client"""
    logger.info(f"🔍 Récupération panier client: {customer_id} [Request-ID: {x_request_id}]")
    
    cart = CartService.get_or_create_cart(db, customer_id=customer_id)
    
    response = schemas.CartResponse.from_orm(cart)
    response.total_items = cart.total_items
    response.total_price = cart.total_price
    return response

@router.get("/session/{session_id}", response_model=schemas.CartResponse)
def get_session_cart(
    session_id: str,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Récupérer le panier d'une session invité"""
    logger.info(f"🔍 Récupération panier session: {session_id} [Request-ID: {x_request_id}]")
    
    cart = CartService.get_or_create_cart(db, session_id=session_id)
    
    response = schemas.CartResponse.from_orm(cart)
    response.total_items = cart.total_items
    response.total_price = cart.total_price
    return response

@router.get("/{cart_id}", response_model=schemas.CartResponse)
def get_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Récupérer un panier par ID"""
    logger.info(f"🔍 Récupération panier: {cart_id} [Request-ID: {x_request_id}]")
    
    cart = CartService.get_cart(db, cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Cart not found",
                "message": "Panier non trouvé",
                "service": "cart-api"
            }
        )
    
    response = schemas.CartResponse.from_orm(cart)
    response.total_items = cart.total_items
    response.total_price = cart.total_price
    return response

@router.post("/{cart_id}/items", response_model=schemas.CartItemResponse)
async def add_to_cart(
    cart_id: int,
    item_data: schemas.AddToCartRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """➕ Ajouter un produit au panier"""
    logger.info(f"➕ Ajout produit {item_data.product_id} (qty: {item_data.quantity}) au panier {cart_id} [Request-ID: {x_request_id}]")
    
    try:
        cart_item = await CartItemService.add_to_cart(db, cart_id, item_data)
        logger.info(f"✅ Produit ajouté au panier {cart_id} [Request-ID: {x_request_id}]")
        
        response = schemas.CartItemResponse.from_orm(cart_item)
        response.subtotal = cart_item.subtotal
        return response
        
    except ValueError as e:
        logger.warning(f"⚠️ Erreur validation ajout panier: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation error",
                "message": str(e),
                "service": "cart-api"
            }
        )
    except ExternalServiceError as e:
        logger.error(f"❌ Erreur service externe: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "External service error",
                "message": "Service temporairement indisponible",
                "service": "cart-api"
            }
        )

@router.put("/{cart_id}/items/{product_id}", response_model=schemas.CartItemResponse)
async def update_cart_item(
    cart_id: int,
    product_id: int,
    update_data: schemas.UpdateCartItemRequest,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """✏️ Mettre à jour un élément du panier"""
    logger.info(f"✏️ Mise à jour produit {product_id} dans panier {cart_id} [Request-ID: {x_request_id}]")
    
    try:
        cart_item = await CartItemService.update_cart_item(db, cart_id, product_id, update_data)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Cart item not found",
                    "message": "Élément du panier non trouvé",
                    "service": "cart-api"
                }
            )
        
        response = schemas.CartItemResponse.from_orm(cart_item)
        response.subtotal = cart_item.subtotal
        return response
        
    except ValueError as e:
        logger.warning(f"⚠️ Erreur validation mise à jour: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation error",
                "message": str(e),
                "service": "cart-api"
            }
        )

@router.delete("/{cart_id}/items/{product_id}")
def remove_from_cart(
    cart_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🗑️ Retirer un produit du panier"""
    logger.info(f"🗑️ Suppression produit {product_id} du panier {cart_id} [Request-ID: {x_request_id}]")
    
    success = CartItemService.remove_from_cart(db, cart_id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Cart item not found",
                "message": "Élément du panier non trouvé",
                "service": "cart-api"
            }
        )
    
    logger.info(f"✅ Produit retiré du panier {cart_id} [Request-ID: {x_request_id}]")
    return {"message": "Produit retiré du panier"}

@router.delete("/{cart_id}/clear")
def clear_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🧹 Vider un panier"""
    logger.info(f"🧹 Vidage panier {cart_id} [Request-ID: {x_request_id}]")
    
    success = CartService.clear_cart(db, cart_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Cart not found",
                "message": "Panier non trouvé",
                "service": "cart-api"
            }
        )
    
    logger.info(f"✅ Panier {cart_id} vidé [Request-ID: {x_request_id}]")
    return {"message": "Panier vidé"}

@router.post("/{cart_id}/validate", response_model=schemas.CartValidationResponse)
async def validate_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """✔️ Valider un panier (stocks, prix, etc.)"""
    logger.info(f"✔️ Validation panier {cart_id} [Request-ID: {x_request_id}]")
    
    validation = await CartService.validate_cart(db, cart_id)
    
    if validation.is_valid:
        logger.info(f"✅ Panier {cart_id} valide [Request-ID: {x_request_id}]")
    else:
        logger.warning(f"⚠️ Panier {cart_id} invalide: {validation.issues} [Request-ID: {x_request_id}]")
    
    return validation

@router.get("/stats/summary", response_model=schemas.CartStats)
def get_cart_statistics(
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📊 Statistiques des paniers"""
    logger.info(f"📊 Récupération statistiques paniers [Request-ID: {x_request_id}]")
    
    stats = CartStatsService.get_cart_stats(db)
    return stats 