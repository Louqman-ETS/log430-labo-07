from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import Optional, List
import httpx
import os
import logging
from decimal import Decimal

from . import models, schemas

logger = logging.getLogger(__name__)

# Configuration des services externes
PRODUCTS_API_URL = os.getenv("PRODUCTS_API_URL", "http://products-api:8001")
STOCK_API_URL = os.getenv("STOCK_API_URL", "http://stock-api:8004")

class ExternalServiceError(Exception):
    """Exception pour les erreurs de services externes"""
    pass

class ProductService:
    """Service pour interagir avec l'API Products"""
    
    @staticmethod
    async def get_product(product_id: int) -> Optional[schemas.ProductInfo]:
        """Récupère les informations d'un produit"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{PRODUCTS_API_URL}/api/v1/products/{product_id}")
                
                if response.status_code == 404:
                    return None
                elif response.status_code != 200:
                    raise ExternalServiceError(f"Products API error: {response.status_code}")
                
                product_data = response.json()
                return schemas.ProductInfo(**product_data)
                
        except httpx.RequestError as e:
            logger.error(f"❌ Erreur communication Products API: {str(e)}")
            raise ExternalServiceError(f"Cannot connect to Products API: {str(e)}")
    
    @staticmethod
    async def get_products(product_ids: List[int]) -> List[schemas.ProductInfo]:
        """Récupère les informations de plusieurs produits"""
        products = []
        for product_id in product_ids:
            product = await ProductService.get_product(product_id)
            if product:
                products.append(product)
        return products

class StockService:
    """Service pour interagir avec l'API Stock"""
    
    @staticmethod
    async def check_stock(product_id: int, quantity: int) -> schemas.StockCheckResponse:
        """Vérifie la disponibilité du stock"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{STOCK_API_URL}/api/v1/products/{product_id}/stock")
                
                if response.status_code == 404:
                    return schemas.StockCheckResponse(
                        product_id=product_id,
                        available_stock=0,
                        is_available=False
                    )
                elif response.status_code != 200:
                    raise ExternalServiceError(f"Stock API error: {response.status_code}")
                
                stock_data = response.json()
                available_stock = stock_data.get("stock_quantity", 0)
                
                return schemas.StockCheckResponse(
                    product_id=product_id,
                    available_stock=available_stock,
                    is_available=available_stock >= quantity
                )
                
        except httpx.RequestError as e:
            logger.error(f"❌ Erreur communication Stock API: {str(e)}")
            # En cas d'erreur, on assume que le produit est disponible (fallback)
            return schemas.StockCheckResponse(
                product_id=product_id,
                available_stock=999,
                is_available=True
            )

class CartService:
    """Service pour la gestion des paniers"""
    
    @staticmethod
    def get_cart(db: Session, cart_id: int) -> Optional[models.Cart]:
        """Récupère un panier par son ID"""
        return db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    
    @staticmethod
    def get_cart_by_customer(db: Session, customer_id: int) -> Optional[models.Cart]:
        """Récupère le panier actif d'un client"""
        return db.query(models.Cart).filter(
            and_(models.Cart.customer_id == customer_id, models.Cart.is_active == True)
        ).first()
    
    @staticmethod
    def get_cart_by_session(db: Session, session_id: str) -> Optional[models.Cart]:
        """Récupère le panier d'une session invité"""
        return db.query(models.Cart).filter(
            and_(models.Cart.session_id == session_id, models.Cart.is_active == True)
        ).first()
    
    @staticmethod
    def create_cart(db: Session, cart_data: schemas.CartCreate) -> models.Cart:
        """Crée un nouveau panier"""
        # Définir une expiration par défaut (30 jours)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        db_cart = models.Cart(
            customer_id=cart_data.customer_id,
            session_id=cart_data.session_id,
            expires_at=expires_at
        )
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)
        return db_cart
    
    @staticmethod
    def get_or_create_cart(db: Session, customer_id: Optional[int] = None, session_id: Optional[str] = None) -> models.Cart:
        """Récupère ou crée un panier pour un client ou une session"""
        if customer_id:
            cart = CartService.get_cart_by_customer(db, customer_id)
        elif session_id:
            cart = CartService.get_cart_by_session(db, session_id)
        else:
            raise ValueError("customer_id ou session_id requis")
        
        if not cart:
            cart_data = schemas.CartCreate(customer_id=customer_id, session_id=session_id)
            cart = CartService.create_cart(db, cart_data)
        
        return cart
    
    @staticmethod
    def clear_cart(db: Session, cart_id: int) -> bool:
        """Vide un panier"""
        cart = CartService.get_cart(db, cart_id)
        if not cart:
            return False
        
        # Supprimer tous les items
        db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
        cart.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def deactivate_cart(db: Session, cart_id: int) -> bool:
        """Désactive un panier"""
        cart = CartService.get_cart(db, cart_id)
        if not cart:
            return False
        
        cart.is_active = False
        cart.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    async def validate_cart(db: Session, cart_id: int) -> schemas.CartValidationResponse:
        """Valide un panier (vérification stock, prix, etc.)"""
        cart = CartService.get_cart(db, cart_id)
        if not cart:
            return schemas.CartValidationResponse(
                is_valid=False,
                total_price=Decimal('0.00'),
                issues=["Panier non trouvé"]
            )
        
        issues = []
        unavailable_items = []
        total_price = Decimal('0.00')
        
        for item in cart.items:
            # Vérifier le stock
            stock_check = await StockService.check_stock(item.product_id, item.quantity)
            if not stock_check.is_available:
                issues.append(f"Produit {item.product_id}: stock insuffisant")
                unavailable_items.append(item.product_id)
            
            # Vérifier le produit existe toujours
            product = await ProductService.get_product(item.product_id)
            if not product:
                issues.append(f"Produit {item.product_id}: non disponible")
                unavailable_items.append(item.product_id)
            else:
                total_price += item.subtotal
        
        return schemas.CartValidationResponse(
            is_valid=len(issues) == 0,
            total_price=total_price,
            issues=issues,
            unavailable_items=unavailable_items
        )

class CartItemService:
    """Service pour la gestion des éléments de panier"""
    
    @staticmethod
    def get_cart_item(db: Session, cart_id: int, product_id: int) -> Optional[models.CartItem]:
        """Récupère un élément spécifique du panier"""
        return db.query(models.CartItem).filter(
            and_(models.CartItem.cart_id == cart_id, models.CartItem.product_id == product_id)
        ).first()
    
    @staticmethod
    async def add_to_cart(db: Session, cart_id: int, item_data: schemas.AddToCartRequest) -> models.CartItem:
        """Ajoute un produit au panier"""
        # Vérifier que le produit existe et récupérer son prix
        product = await ProductService.get_product(item_data.product_id)
        if not product:
            raise ValueError(f"Produit {item_data.product_id} non trouvé")
        
        # Vérifier le stock
        stock_check = await StockService.check_stock(item_data.product_id, item_data.quantity)
        if not stock_check.is_available:
            raise ValueError(f"Stock insuffisant pour le produit {item_data.product_id}")
        
        # Vérifier si l'item existe déjà dans le panier
        existing_item = CartItemService.get_cart_item(db, cart_id, item_data.product_id)
        
        if existing_item:
            # Mettre à jour la quantité
            new_quantity = existing_item.quantity + item_data.quantity
            
            # Vérifier le stock pour la nouvelle quantité
            stock_check = await StockService.check_stock(item_data.product_id, new_quantity)
            if not stock_check.is_available:
                raise ValueError(f"Stock insuffisant pour la quantité totale {new_quantity}")
            
            existing_item.quantity = new_quantity
            existing_item.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_item)
            
            # Mettre à jour le timestamp du panier
            cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
            if cart:
                cart.updated_at = datetime.utcnow()
                db.commit()
            
            return existing_item
        else:
            # Créer un nouvel item
            db_item = models.CartItem(
                cart_id=cart_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.prix
            )
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            
            # Mettre à jour le timestamp du panier
            cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
            if cart:
                cart.updated_at = datetime.utcnow()
                db.commit()
            
            return db_item
    
    @staticmethod
    async def update_cart_item(db: Session, cart_id: int, product_id: int, update_data: schemas.UpdateCartItemRequest) -> Optional[models.CartItem]:
        """Met à jour un élément du panier"""
        cart_item = CartItemService.get_cart_item(db, cart_id, product_id)
        if not cart_item:
            return None
        
        # Vérifier le stock pour la nouvelle quantité
        stock_check = await StockService.check_stock(product_id, update_data.quantity)
        if not stock_check.is_available:
            raise ValueError(f"Stock insuffisant pour la quantité {update_data.quantity}")
        
        cart_item.quantity = update_data.quantity
        cart_item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cart_item)
        
        # Mettre à jour le timestamp du panier
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
        if cart:
            cart.updated_at = datetime.utcnow()
            db.commit()
        
        return cart_item
    
    @staticmethod
    def remove_from_cart(db: Session, cart_id: int, product_id: int) -> bool:
        """Retire un produit du panier"""
        cart_item = CartItemService.get_cart_item(db, cart_id, product_id)
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        
        # Mettre à jour le timestamp du panier
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
        if cart:
            cart.updated_at = datetime.utcnow()
            db.commit()
        
        return True

class CartStatsService:
    """Service pour les statistiques des paniers"""
    
    @staticmethod
    def get_cart_stats(db: Session) -> schemas.CartStats:
        """Récupère les statistiques des paniers"""
        total_active = db.query(func.count(models.Cart.id)).filter(models.Cart.is_active == True).scalar() or 0
        
        total_items = db.query(func.sum(models.CartItem.quantity)).join(models.Cart).filter(
            models.Cart.is_active == True
        ).scalar() or 0
        
        # Calcul de la valeur moyenne des paniers
        avg_value = db.query(func.avg(
            func.sum(models.CartItem.quantity * models.CartItem.unit_price)
        )).join(models.Cart).filter(models.Cart.is_active == True).group_by(models.Cart.id).scalar() or Decimal('0.00')
        
        # Paniers abandonnés aujourd'hui (non mis à jour depuis 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        abandoned_today = db.query(func.count(models.Cart.id)).filter(
            and_(
                models.Cart.is_active == True,
                models.Cart.updated_at < yesterday,
                models.Cart.created_at >= yesterday
            )
        ).scalar() or 0
        
        return schemas.CartStats(
            total_active_carts=total_active,
            total_items_in_carts=total_items,
            average_cart_value=Decimal(str(avg_value)) if avg_value else Decimal('0.00'),
            abandoned_carts_today=abandoned_today
        ) 