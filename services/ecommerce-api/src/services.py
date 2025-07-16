import os
import logging
import httpx
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import hashlib
import secrets
import jwt
from passlib.context import CryptContext
from decimal import Decimal

import src.models as models
import src.schemas as schemas

logger = logging.getLogger(__name__)

# Configuration des services externes
PRODUCTS_API_URL = os.getenv("PRODUCTS_API_URL", "http://inventory-api:8001")
STOCK_API_URL = os.getenv("STOCK_API_URL", "http://inventory-api:8001")
KONG_API_KEY = os.getenv("KONG_API_KEY", "admin-api-key-12345")

# Configuration pour l'authentification
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Headers pour Kong
KONG_HEADERS = {
    "apikey": KONG_API_KEY,
    "Content-Type": "application/json"
}


class ExternalServiceError(Exception):
    """Exception pour les erreurs de services externes"""

    pass


# ============================================================================
# EXTERNAL SERVICES
# ============================================================================


class ProductService:
    """Service pour interagir avec l'API Products"""

    @staticmethod
    async def get_product(product_id: int) -> Optional[schemas.ProductInfo]:
        """Récupère les informations d'un produit"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{PRODUCTS_API_URL}/api/v1/products/{product_id}",
                    headers=KONG_HEADERS
                )

                if response.status_code == 404:
                    return None
                elif response.status_code != 200:
                    raise ExternalServiceError(
                        f"Products API error: {response.status_code}"
                    )

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
                response = await client.get(
                    f"{STOCK_API_URL}/api/v1/products/{product_id}/stock",
                    headers=KONG_HEADERS
                )

                if response.status_code == 404:
                    return schemas.StockCheckResponse(
                        product_id=product_id, available_stock=0, is_available=False
                    )
                elif response.status_code != 200:
                    raise ExternalServiceError(
                        f"Stock API error: {response.status_code}"
                    )

                stock_data = response.json()
                available_stock = stock_data.get("quantite_stock", 0)

                print(
                    f"🔍 Stock check - Product {product_id}: available={available_stock} (type: {type(available_stock)}), requested={quantity} (type: {type(quantity)}), is_available={available_stock >= quantity}"
                )
                logger.info(
                    f"🔍 Stock check - Product {product_id}: available={available_stock}, requested={quantity}, is_available={available_stock >= quantity}"
                )

                return schemas.StockCheckResponse(
                    product_id=product_id,
                    available_stock=available_stock,
                    is_available=available_stock >= quantity,
                )

        except httpx.RequestError as e:
            logger.error(f"❌ Erreur communication Stock API: {str(e)}")
            # En cas d'erreur, on assume que le produit est disponible (fallback)
            return schemas.StockCheckResponse(
                product_id=product_id, available_stock=999, is_available=True
            )


# ============================================================================
# CUSTOMER SERVICES
# ============================================================================


class CustomerService:
    """Service pour la gestion des clients"""

    def __init__(self, db: Session):
        self.db = db

    def get_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True,
    ) -> List[models.Customer]:
        """Récupère tous les clients avec pagination et recherche"""
        query = self.db.query(models.Customer)

        if active_only:
            query = query.filter(models.Customer.is_active == True)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (models.Customer.first_name.ilike(search_term))
                | (models.Customer.last_name.ilike(search_term))
                | (models.Customer.email.ilike(search_term))
            )

        return query.offset(skip).limit(limit).all()

    def get_customer(self, customer_id: int) -> Optional[models.Customer]:
        """Récupère un client par ID"""
        return (
            self.db.query(models.Customer)
            .filter(models.Customer.id == customer_id)
            .first()
        )

    def get_customer_by_email(self, email: str) -> Optional[models.Customer]:
        """Récupère un client par email"""
        return (
            self.db.query(models.Customer)
            .filter(models.Customer.email == email)
            .first()
        )

    def create_customer(self, customer: schemas.CustomerCreate) -> models.Customer:
        """Crée un nouveau client"""
        # Vérifier si l'email existe déjà
        if self.get_customer_by_email(customer.email):
            raise ValueError("Email already registered")

        # Créer le client
        db_customer = models.Customer(
            email=customer.email,
            first_name=customer.first_name,
            last_name=customer.last_name,
            phone=customer.phone,
            date_of_birth=customer.date_of_birth,
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)

        # Créer l'authentification
        hashed_password = pwd_context.hash(customer.password)
        db_auth = models.CustomerAuth(
            customer_id=db_customer.id, password_hash=hashed_password
        )
        self.db.add(db_auth)
        self.db.commit()

        return db_customer

    def update_customer(
        self, customer_id: int, customer: schemas.CustomerUpdate
    ) -> Optional[models.Customer]:
        """Met à jour un client"""
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return None

        update_data = customer.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)

        db_customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: int) -> bool:
        """Supprime un client"""
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return False

        # Supprimer d'abord l'authentification
        db_auth = (
            self.db.query(models.CustomerAuth)
            .filter(models.CustomerAuth.customer_id == customer_id)
            .first()
        )
        if db_auth:
            self.db.delete(db_auth)

        # Puis supprimer le client
        self.db.delete(db_customer)
        self.db.commit()
        return True

    def get_customer_with_addresses(
        self, customer_id: int
    ) -> Optional[models.Customer]:
        """Récupère un client avec ses adresses"""
        return (
            self.db.query(models.Customer)
            .filter(models.Customer.id == customer_id)
            .first()
        )

    def get_customer_stats(self) -> schemas.CustomerStats:
        """Récupère les statistiques des clients"""
        total_customers = self.db.query(models.Customer).count()
        active_customers = (
            self.db.query(models.Customer)
            .filter(models.Customer.is_active == True)
            .count()
        )

        # Clients créés aujourd'hui
        today = datetime.utcnow().date()
        new_customers_today = (
            self.db.query(models.Customer)
            .filter(func.date(models.Customer.created_at) == today)
            .count()
        )

        # Clients avec commandes
        customers_with_orders = (
            self.db.query(models.Customer).join(models.Order).distinct().count()
        )

        return schemas.CustomerStats(
            total_customers=total_customers,
            active_customers=active_customers,
            new_customers_today=new_customers_today,
            customers_with_orders=customers_with_orders,
        )


class AddressService:
    """Service pour la gestion des adresses"""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_addresses(self, customer_id: int) -> List[models.Address]:
        """Récupère les adresses d'un client"""
        return (
            self.db.query(models.Address)
            .filter(models.Address.customer_id == customer_id)
            .all()
        )

    def get_address(
        self, customer_id: int, address_id: int
    ) -> Optional[models.Address]:
        """Récupère une adresse spécifique"""
        return (
            self.db.query(models.Address)
            .filter(
                and_(
                    models.Address.id == address_id,
                    models.Address.customer_id == customer_id,
                )
            )
            .first()
        )

    def create_address(
        self, customer_id: int, address: schemas.AddressCreate
    ) -> models.Address:
        """Crée une nouvelle adresse"""
        db_address = models.Address(customer_id=customer_id, **address.dict())
        self.db.add(db_address)
        self.db.commit()
        self.db.refresh(db_address)
        return db_address

    def update_address(
        self, customer_id: int, address_id: int, address: schemas.AddressUpdate
    ) -> Optional[models.Address]:
        """Met à jour une adresse"""
        db_address = self.get_address(customer_id, address_id)
        if not db_address:
            return None

        update_data = address.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_address, field, value)

        self.db.commit()
        self.db.refresh(db_address)
        return db_address

    def delete_address(self, customer_id: int, address_id: int) -> bool:
        """Supprime une adresse"""
        db_address = self.get_address(customer_id, address_id)
        if not db_address:
            return False

        self.db.delete(db_address)
        self.db.commit()
        return True


class AuthService:
    """Service pour l'authentification"""

    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        """Crée un token d'accès"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register_customer(
        self, customer: schemas.CustomerRegister
    ) -> schemas.LoginResponse:
        """Inscrit un nouveau client"""
        # Créer le client
        customer_service = CustomerService(self.db)
        db_customer = customer_service.create_customer(customer)

        # Créer le token
        access_token = self.create_access_token(data={"sub": str(db_customer.id)})

        return schemas.LoginResponse(
            customer=schemas.CustomerResponse.from_orm(db_customer),
            token=schemas.Token(
                access_token=access_token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ),
        )

    def login_customer(
        self, login_data: schemas.CustomerLogin
    ) -> schemas.LoginResponse:
        """Connecte un client"""
        customer_service = CustomerService(self.db)
        db_customer = customer_service.get_customer_by_email(login_data.email)

        if not db_customer or not db_customer.auth:
            raise ValueError("Invalid email or password")

        if not self.verify_password(
            login_data.password, db_customer.auth.password_hash
        ):
            raise ValueError("Invalid email or password")

        if not db_customer.is_active:
            raise ValueError("Account is deactivated")

        # Mettre à jour la dernière connexion
        db_customer.auth.last_login = datetime.utcnow()
        db_customer.auth.login_attempts = 0
        self.db.commit()

        # Créer le token
        access_token = self.create_access_token(data={"sub": str(db_customer.id)})

        return schemas.LoginResponse(
            customer=schemas.CustomerResponse.from_orm(db_customer),
            token=schemas.Token(
                access_token=access_token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ),
        )

    def change_password(
        self, customer_id: int, password_change: schemas.PasswordChange
    ) -> None:
        """Change le mot de passe d'un client"""
        db_customer = (
            self.db.query(models.Customer)
            .filter(models.Customer.id == customer_id)
            .first()
        )
        if not db_customer or not db_customer.auth:
            raise ValueError("Customer not found")

        if not self.verify_password(
            password_change.current_password, db_customer.auth.password_hash
        ):
            raise ValueError("Current password is incorrect")

        # Mettre à jour le mot de passe
        db_customer.auth.password_hash = pwd_context.hash(password_change.new_password)
        self.db.commit()


# ============================================================================
# CART SERVICES
# ============================================================================


class CartService:
    """Service pour la gestion des paniers"""

    def __init__(self, db: Session):
        self.db = db

    def get_carts(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> List[models.Cart]:
        """Récupère les paniers avec filtres"""
        query = self.db.query(models.Cart)

        if customer_id:
            query = query.filter(models.Cart.customer_id == customer_id)
        if session_id:
            query = query.filter(models.Cart.session_id == session_id)

        return query.offset(skip).limit(limit).all()

    def get_cart(self, cart_id: int) -> Optional[models.Cart]:
        """Récupère un panier par ID"""
        return self.db.query(models.Cart).filter(models.Cart.id == cart_id).first()

    def get_cart_by_customer(self, customer_id: int) -> Optional[models.Cart]:
        """Récupère le panier actif d'un client"""
        return (
            self.db.query(models.Cart)
            .filter(
                and_(
                    models.Cart.customer_id == customer_id,
                    models.Cart.is_active == True,
                )
            )
            .first()
        )

    def get_cart_by_session(self, session_id: str) -> Optional[models.Cart]:
        """Récupère le panier d'une session invité"""
        return (
            self.db.query(models.Cart)
            .filter(
                and_(
                    models.Cart.session_id == session_id, models.Cart.is_active == True
                )
            )
            .first()
        )

    def create_cart(self, cart: schemas.CartCreate) -> models.Cart:
        """Crée un nouveau panier"""
        expires_at = datetime.utcnow() + timedelta(days=30)

        db_cart = models.Cart(
            customer_id=cart.customer_id,
            session_id=cart.session_id,
            expires_at=expires_at,
        )
        self.db.add(db_cart)
        self.db.commit()
        self.db.refresh(db_cart)
        return db_cart

    def update_cart(
        self, cart_id: int, cart: schemas.CartCreate
    ) -> Optional[models.Cart]:
        """Met à jour un panier"""
        db_cart = self.get_cart(cart_id)
        if not db_cart:
            return None

        update_data = cart.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cart, field, value)

        db_cart.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_cart)
        return db_cart

    def delete_cart(self, cart_id: int) -> bool:
        """Supprime un panier"""
        db_cart = self.get_cart(cart_id)
        if not db_cart:
            return False

        self.db.delete(db_cart)
        self.db.commit()
        return True

    def get_customer_carts(self, customer_id: int) -> List[models.Cart]:
        """Récupère tous les paniers d'un client"""
        return (
            self.db.query(models.Cart)
            .filter(models.Cart.customer_id == customer_id)
            .all()
        )

    def get_cart_with_products(self, cart_id: int) -> Optional[models.Cart]:
        """Récupère un panier avec les informations produits"""
        return self.get_cart(cart_id)  # Les relations sont automatiquement chargées

    def clear_cart(self, cart_id: int) -> Optional[models.Cart]:
        """Vide un panier"""
        db_cart = self.get_cart(cart_id)
        if not db_cart:
            return None

        # Supprimer tous les items
        self.db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart_id
        ).delete()
        db_cart.updated_at = datetime.utcnow()
        self.db.commit()
        return db_cart

    def get_cart_items(self, cart_id: int) -> List[models.CartItem]:
        """Récupère tous les éléments d'un panier"""
        return (
            self.db.query(models.CartItem)
            .filter(models.CartItem.cart_id == cart_id)
            .all()
        )

    def get_cart_item(self, cart_id: int, item_id: int) -> Optional[models.CartItem]:
        """Récupère un élément spécifique du panier"""
        return (
            self.db.query(models.CartItem)
            .filter(
                and_(models.CartItem.id == item_id, models.CartItem.cart_id == cart_id)
            )
            .first()
        )

    async def add_item_to_cart(
        self, cart_id: int, item: schemas.AddToCartRequest
    ) -> models.CartItem:
        """Ajoute un élément au panier"""
        logger.info(
            f"Adding item to cart: cart_id={cart_id}, product_id={item.product_id}, quantity={item.quantity}"
        )

        # Vérifier que le panier existe
        cart = self.get_cart(cart_id)
        if not cart:
            logger.error(f"Cart {cart_id} not found")
            raise ValueError("Cart not found")

        # Vérifier le produit
        product = await ProductService.get_product(item.product_id)
        if not product:
            raise ValueError("Product not found")

        # Vérifier le stock
        stock_check = await StockService.check_stock(item.product_id, item.quantity)
        logger.info(
            f"Stock check for product {item.product_id}: available={stock_check.available_stock}, requested={item.quantity}, is_available={stock_check.is_available}"
        )

        if not stock_check.is_available:
            logger.error(f"Insufficient stock for product {item.product_id}")
            raise ValueError(f"Insufficient stock for product {item.product_id}")

        # Vérifier si l'élément existe déjà
        existing_item = (
            self.db.query(models.CartItem)
            .filter(
                and_(
                    models.CartItem.cart_id == cart_id,
                    models.CartItem.product_id == item.product_id,
                )
            )
            .first()
        )

        if existing_item:
            # Mettre à jour la quantité
            existing_item.quantity += item.quantity
            existing_item.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Créer un nouvel élément
            db_item = models.CartItem(
                cart_id=cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.prix,
            )
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item

    def update_cart_item(
        self, cart_id: int, item_id: int, item: schemas.UpdateCartItemRequest
    ) -> Optional[models.CartItem]:
        """Met à jour un élément du panier"""
        db_item = self.get_cart_item(cart_id, item_id)
        if not db_item:
            return None

        if item.quantity is not None:
            db_item.quantity = item.quantity
            db_item.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def remove_cart_item(self, cart_id: int, item_id: int) -> bool:
        """Supprime un élément du panier"""
        db_item = self.get_cart_item(cart_id, item_id)
        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()
        return True

    async def validate_cart(self, cart_id: int) -> schemas.CartValidationResponse:
        """Valide un panier"""
        cart = self.get_cart(cart_id)
        if not cart:
            return schemas.CartValidationResponse(
                is_valid=False, total_price=Decimal("0.00"), issues=["Cart not found"]
            )

        issues = []
        unavailable_items = []
        total_price = Decimal("0.00")

        for item in cart.items:
            # Vérifier le stock
            stock_check = await StockService.check_stock(item.product_id, item.quantity)
            if not stock_check.is_available:
                issues.append(f"Product {item.product_id}: insufficient stock")
                unavailable_items.append(item.product_id)

            # Vérifier le produit existe toujours
            product = await ProductService.get_product(item.product_id)
            if not product:
                issues.append(f"Product {item.product_id}: not available")
                unavailable_items.append(item.product_id)
            else:
                total_price += item.subtotal

        return schemas.CartValidationResponse(
            is_valid=len(issues) == 0,
            total_price=total_price,
            issues=issues,
            unavailable_items=unavailable_items,
        )

    async def check_cart_stock(self, cart_id: int) -> List[schemas.StockCheckResponse]:
        """Vérifie le stock pour tous les éléments d'un panier"""
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError("Cart not found")

        stock_checks = []
        for item in cart.items:
            stock_check = await StockService.check_stock(item.product_id, item.quantity)
            stock_checks.append(stock_check)

        return stock_checks

    def get_cart_stats(self) -> schemas.CartStats:
        """Récupère les statistiques des paniers"""
        total_active_carts = (
            self.db.query(models.Cart).filter(models.Cart.is_active == True).count()
        )
        total_items_in_carts = (
            self.db.query(func.sum(models.CartItem.quantity)).scalar() or 0
        )

        # Calculer la valeur moyenne des paniers
        cart_totals = (
            self.db.query(
                models.Cart.id,
                func.sum(models.CartItem.quantity * models.CartItem.unit_price).label(
                    "total"
                ),
            )
            .join(models.CartItem)
            .group_by(models.Cart.id)
            .all()
        )

        if cart_totals:
            average_cart_value = sum(cart.total for cart in cart_totals) / len(
                cart_totals
            )
        else:
            average_cart_value = Decimal("0.00")

        # Paniers abandonnés aujourd'hui (créés mais pas convertis en commande)
        today = datetime.utcnow().date()
        abandoned_carts_today = (
            self.db.query(models.Cart)
            .filter(
                and_(
                    func.date(models.Cart.created_at) == today,
                    models.Cart.is_active == True,
                )
            )
            .count()
        )

        return schemas.CartStats(
            total_active_carts=total_active_carts,
            total_items_in_carts=total_items_in_carts,
            average_cart_value=average_cart_value,
            abandoned_carts_today=abandoned_carts_today,
        )


# ============================================================================
# ORDER SERVICES
# ============================================================================


class OrderService:
    """Service pour la gestion des commandes"""

    def __init__(self, db: Session):
        self.db = db

    def generate_order_number(self) -> str:
        """Génère un numéro de commande unique"""
        timestamp = int(time.time())
        return f"ORD-{timestamp}"

    def get_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[schemas.OrderStatus] = None,
    ) -> List[models.Order]:
        """Récupère les commandes avec filtres"""
        query = self.db.query(models.Order)

        if customer_id:
            query = query.filter(models.Order.customer_id == customer_id)
        if status:
            query = query.filter(models.Order.status == status)

        return query.offset(skip).limit(limit).all()

    def get_order(self, order_id: int) -> Optional[models.Order]:
        """Récupère une commande par ID"""
        return self.db.query(models.Order).filter(models.Order.id == order_id).first()

    def get_customer_orders(
        self, customer_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Order]:
        """Récupère toutes les commandes d'un client"""
        return (
            self.db.query(models.Order)
            .filter(models.Order.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_order_items(self, order_id: int) -> List[models.OrderItem]:
        """Récupère tous les éléments d'une commande"""
        return (
            self.db.query(models.OrderItem)
            .filter(models.OrderItem.order_id == order_id)
            .all()
        )

    async def process_checkout(
        self, checkout_data: schemas.CheckoutRequest
    ) -> models.Order:
        """Traite une commande de checkout depuis un panier"""
        # Récupérer le panier
        cart_service = CartService(self.db)
        cart = cart_service.get_cart(checkout_data.cart_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty or not found")

        # Valider le panier
        cart_validation = await cart_service.validate_cart(checkout_data.cart_id)
        if not cart_validation.is_valid:
            raise ValueError(f"Cart validation failed: {cart_validation.issues}")

        # Calculer les montants
        subtotal = cart.total_price
        tax_rate = Decimal("0.20")  # 20% TVA
        tax_amount = subtotal * tax_rate
        shipping_amount = Decimal("5.00") if subtotal < 50 else Decimal("0.00")
        total_amount = subtotal + tax_amount + shipping_amount

        # Créer la commande
        order = models.Order(
            order_number=self.generate_order_number(),
            customer_id=checkout_data.customer_id,
            cart_id=checkout_data.cart_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            shipping_address=checkout_data.shipping_address,
            billing_address=checkout_data.billing_address,
        )

        self.db.add(order)
        self.db.flush()

        # Créer les éléments de commande
        for cart_item in cart.items:
            # Récupérer le nom du produit
            product_name = f"Product {cart_item.product_id}"
            try:
                product = await ProductService.get_product(cart_item.product_id)
                if product:
                    product_name = product.nom
            except:
                pass

            order_item = models.OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=product_name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
            )
            self.db.add(order_item)

        # Mettre à jour le stock dans inventory-api
        for cart_item in cart.items:
            try:
                await self.update_stock_after_order(
                    cart_item.product_id, cart_item.quantity
                )
                logger.info(
                    f"Stock updated for product {cart_item.product_id}: -{cart_item.quantity}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to update stock for product {cart_item.product_id}: {str(e)}"
                )
                # On continue même si la mise à jour du stock échoue

        # Désactiver le panier
        cart.is_active = False
        cart.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(order)
        return order

    def update_order_status(
        self, order_id: int, status: schemas.OrderStatus
    ) -> Optional[models.Order]:
        """Met à jour le statut d'une commande"""
        order = self.get_order(order_id)
        if not order:
            return None

        order.status = status
        order.updated_at = datetime.utcnow()

        # Mettre à jour les dates spécifiques selon le statut
        if status == schemas.OrderStatus.CONFIRMED:
            order.confirmed_at = datetime.utcnow()
        elif status == schemas.OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif status == schemas.OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(order)
        return order

    def update_payment_status(
        self, order_id: int, payment_status: schemas.PaymentStatus
    ) -> Optional[models.Order]:
        """Met à jour le statut de paiement d'une commande"""
        order = self.get_order(order_id)
        if not order:
            return None

        order.payment_status = payment_status
        order.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_tracking(self, order_id: int) -> Optional[dict]:
        """Récupère les informations de suivi d'une commande"""
        order = self.get_order(order_id)
        if not order:
            return None

        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status.value,
            "created_at": order.created_at,
            "confirmed_at": order.confirmed_at,
            "shipped_at": order.shipped_at,
            "delivered_at": order.delivered_at,
        }

    def confirm_order(self, order_id: int) -> Optional[models.Order]:
        """Confirme une commande"""
        return self.update_order_status(order_id, schemas.OrderStatus.CONFIRMED)

    def ship_order(
        self, order_id: int, tracking_number: Optional[str] = None
    ) -> Optional[models.Order]:
        """Marque une commande comme expédiée"""
        order = self.update_order_status(order_id, schemas.OrderStatus.SHIPPED)
        # Ici on pourrait ajouter le numéro de suivi à la base de données
        return order

    def deliver_order(self, order_id: int) -> Optional[models.Order]:
        """Marque une commande comme livrée"""
        return self.update_order_status(order_id, schemas.OrderStatus.DELIVERED)

    def cancel_order(
        self, order_id: int, reason: Optional[str] = None
    ) -> Optional[models.Order]:
        """Annule une commande"""
        return self.update_order_status(order_id, schemas.OrderStatus.CANCELLED)

    async def update_stock_after_order(self, product_id: int, quantity: int) -> None:
        """Met à jour le stock après une commande"""
        try:
            async with httpx.AsyncClient() as client:
                # Réduire le stock en utilisant l'endpoint approprié
                params = {
                    "quantity": quantity,
                    "raison": "commande_ecommerce",
                    "reference": f"order_{int(time.time())}",
                }
                update_response = await client.put(
                    f"{STOCK_API_URL}/api/v1/stock/products/{product_id}/stock/reduce",
                    params=params,
                )

                if update_response.status_code != 200:
                    raise ExternalServiceError(
                        f"Failed to update stock for product {product_id}"
                    )

                result = update_response.json()
                logger.info(f"Stock reduced for product {product_id}: {result}")

        except httpx.RequestError as e:
            logger.error(f"Error updating stock for product {product_id}: {str(e)}")
            raise ExternalServiceError(f"Stock update failed: {str(e)}")

    def get_order_stats(self) -> schemas.OrderStats:
        """Récupère les statistiques des commandes"""
        total_orders = self.db.query(models.Order).count()
        pending_orders = (
            self.db.query(models.Order)
            .filter(models.Order.status == schemas.OrderStatus.PENDING)
            .count()
        )
        completed_orders = (
            self.db.query(models.Order)
            .filter(models.Order.status == schemas.OrderStatus.DELIVERED)
            .count()
        )

        # Revenu total
        total_revenue = self.db.query(
            func.sum(models.Order.total_amount)
        ).scalar() or Decimal("0.00")

        # Commandes créées aujourd'hui
        today = datetime.utcnow().date()
        orders_today = (
            self.db.query(models.Order)
            .filter(func.date(models.Order.created_at) == today)
            .count()
        )

        return schemas.OrderStats(
            total_orders=total_orders,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            total_revenue=total_revenue,
            orders_today=orders_today,
        )
