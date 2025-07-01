from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os

from . import models, schemas

# Configuration pour l'authentification
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service pour l'authentification des clients"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe contre son hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Génère un hash pour un mot de passe"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crée un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[schemas.TokenData]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id: int = payload.get("sub")
            if customer_id is None:
                return None
            token_data = schemas.TokenData(customer_id=customer_id)
        except JWTError:
            return None
        return token_data

class CustomerService:
    """Service pour la gestion des clients"""
    
    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
        """Récupère un client par son ID"""
        return db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    
    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
        """Récupère un client par son email"""
        return db.query(models.Customer).filter(models.Customer.email == email).first()
    
    @staticmethod
    def get_customers(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[models.Customer]:
        """Récupère une liste de clients avec pagination"""
        query = db.query(models.Customer)
        if active_only:
            query = query.filter(models.Customer.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_customer(db: Session, customer: schemas.CustomerRegister) -> models.Customer:
        """Crée un nouveau client avec authentification"""
        # Créer le client
        db_customer = models.Customer(
            email=customer.email,
            first_name=customer.first_name,
            last_name=customer.last_name,
            phone=customer.phone,
            date_of_birth=customer.date_of_birth
        )
        db.add(db_customer)
        db.flush()  # Pour obtenir l'ID
        
        # Créer les données d'authentification
        hashed_password = AuthService.get_password_hash(customer.password)
        db_auth = models.CustomerAuth(
            customer_id=db_customer.id,
            password_hash=hashed_password
        )
        db.add(db_auth)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def authenticate_customer(db: Session, email: str, password: str) -> Optional[models.Customer]:
        """Authentifie un client"""
        customer = CustomerService.get_customer_by_email(db, email)
        if not customer or not customer.is_active:
            return None
        
        auth = db.query(models.CustomerAuth).filter(
            models.CustomerAuth.customer_id == customer.id
        ).first()
        
        if not auth or auth.is_locked:
            return None
        
        if not AuthService.verify_password(password, auth.password_hash):
            # Incrémenter les tentatives de connexion
            auth.login_attempts += 1
            if auth.login_attempts >= 5:
                auth.is_locked = True
            db.commit()
            return None
        
        # Connexion réussie - réinitialiser les tentatives
        auth.login_attempts = 0
        auth.last_login = datetime.utcnow()
        db.commit()
        return customer
    
    @staticmethod
    def update_customer(db: Session, customer_id: int, customer_update: schemas.CustomerUpdate) -> Optional[models.Customer]:
        """Met à jour un client"""
        db_customer = CustomerService.get_customer(db, customer_id)
        if not db_customer:
            return None
        
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db_customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def deactivate_customer(db: Session, customer_id: int) -> bool:
        """Désactive un client"""
        db_customer = CustomerService.get_customer(db, customer_id)
        if not db_customer:
            return False
        
        db_customer.is_active = False
        db_customer.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def change_password(db: Session, customer_id: int, password_change: schemas.PasswordChange) -> bool:
        """Change le mot de passe d'un client"""
        customer = CustomerService.get_customer(db, customer_id)
        if not customer:
            return False
        
        auth = db.query(models.CustomerAuth).filter(
            models.CustomerAuth.customer_id == customer_id
        ).first()
        
        if not auth:
            return False
        
        # Vérifier l'ancien mot de passe
        if not AuthService.verify_password(password_change.current_password, auth.password_hash):
            return False
        
        # Mettre à jour le mot de passe
        auth.password_hash = AuthService.get_password_hash(password_change.new_password)
        db.commit()
        return True

class AddressService:
    """Service pour la gestion des adresses"""
    
    @staticmethod
    def get_customer_addresses(db: Session, customer_id: int) -> List[models.Address]:
        """Récupère toutes les adresses d'un client"""
        return db.query(models.Address).filter(models.Address.customer_id == customer_id).all()
    
    @staticmethod
    def get_address(db: Session, address_id: int, customer_id: int) -> Optional[models.Address]:
        """Récupère une adresse spécifique d'un client"""
        return db.query(models.Address).filter(
            and_(models.Address.id == address_id, models.Address.customer_id == customer_id)
        ).first()
    
    @staticmethod
    def create_address(db: Session, customer_id: int, address: schemas.AddressCreate) -> models.Address:
        """Crée une nouvelle adresse pour un client"""
        # Si c'est la première adresse ou marquée par défaut, la définir comme défaut
        if address.is_default:
            # Retirer le statut par défaut des autres adresses
            db.query(models.Address).filter(
                and_(models.Address.customer_id == customer_id, models.Address.type == address.type)
            ).update({"is_default": False})
        
        db_address = models.Address(
            customer_id=customer_id,
            **address.dict()
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address
    
    @staticmethod
    def update_address(db: Session, address_id: int, customer_id: int, address_update: schemas.AddressUpdate) -> Optional[models.Address]:
        """Met à jour une adresse"""
        db_address = AddressService.get_address(db, address_id, customer_id)
        if not db_address:
            return None
        
        update_data = address_update.dict(exclude_unset=True)
        
        # Gérer le statut par défaut
        if update_data.get("is_default", False):
            db.query(models.Address).filter(
                and_(
                    models.Address.customer_id == customer_id, 
                    models.Address.type == (update_data.get("type", db_address.type))
                )
            ).update({"is_default": False})
        
        for field, value in update_data.items():
            setattr(db_address, field, value)
        
        db.commit()
        db.refresh(db_address)
        return db_address
    
    @staticmethod
    def delete_address(db: Session, address_id: int, customer_id: int) -> bool:
        """Supprime une adresse"""
        db_address = AddressService.get_address(db, address_id, customer_id)
        if not db_address:
            return False
        
        db.delete(db_address)
        db.commit()
        return True

class StatsService:
    """Service pour les statistiques des clients"""
    
    @staticmethod
    def get_customer_stats(db: Session) -> schemas.CustomerStats:
        """Récupère les statistiques des clients"""
        total = db.query(func.count(models.Customer.id)).scalar() or 0
        active = db.query(func.count(models.Customer.id)).filter(models.Customer.is_active == True).scalar() or 0
        
        today = datetime.utcnow().date()
        new_today = db.query(func.count(models.Customer.id)).filter(
            func.date(models.Customer.created_at) == today
        ).scalar() or 0
        
        return schemas.CustomerStats(
            total_customers=total,
            active_customers=active,
            new_customers_today=new_today,
            customers_with_orders=0  # À implémenter avec l'API Orders
        ) 