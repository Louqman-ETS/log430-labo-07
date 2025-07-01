from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import logging

from ...database import get_db
from ...services import CustomerService, AuthService, StatsService, ACCESS_TOKEN_EXPIRE_MINUTES
from ... import schemas

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.CustomerResponse:
    """Dépendance pour obtenir le client authentifié"""
    token_data = AuthService.verify_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    customer = CustomerService.get_customer(db, customer_id=token_data.customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return schemas.CustomerResponse.from_orm(customer)

@router.post("/register", response_model=schemas.LoginResponse, status_code=status.HTTP_201_CREATED)
def register_customer(
    customer_data: schemas.CustomerRegister,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🧑‍💼 Créer un nouveau compte client"""
    logger.info(f"📝 Inscription nouveau client: {customer_data.email} [Request-ID: {x_request_id}]")
    
    # Vérifier si l'email existe déjà
    existing_customer = CustomerService.get_customer_by_email(db, customer_data.email)
    if existing_customer:
        logger.warning(f"❌ Email déjà utilisé: {customer_data.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Email already registered",
                "message": "Un compte existe déjà avec cette adresse email",
                "service": "customers-api"
            }
        )
    
    try:
        # Créer le client
        customer = CustomerService.create_customer(db, customer_data)
        
        # Créer un token d'accès
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(customer.id)},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ Client créé avec succès: {customer.email} (ID: {customer.id}) [Request-ID: {x_request_id}]")
        
        return schemas.LoginResponse(
            customer=schemas.CustomerResponse.from_orm(customer),
            token=schemas.Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du client: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Registration failed",
                "message": "Erreur lors de la création du compte",
                "service": "customers-api"
            }
        )

@router.post("/login", response_model=schemas.LoginResponse)
def login_customer(
    login_data: schemas.CustomerLogin,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔐 Connexion client"""
    logger.info(f"🔑 Tentative de connexion: {login_data.email} [Request-ID: {x_request_id}]")
    
    customer = CustomerService.authenticate_customer(db, login_data.email, login_data.password)
    if not customer:
        logger.warning(f"❌ Échec de connexion: {login_data.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid credentials",
                "message": "Email ou mot de passe incorrect",
                "service": "customers-api"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer un token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(customer.id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Connexion réussie: {customer.email} (ID: {customer.id}) [Request-ID: {x_request_id}]")
    
    return schemas.LoginResponse(
        customer=schemas.CustomerResponse.from_orm(customer),
        token=schemas.Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )

@router.get("/me", response_model=schemas.CustomerResponse)
def get_current_customer_profile(
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    x_request_id: Optional[str] = Header(None)
):
    """👤 Obtenir le profil du client authentifié"""
    logger.info(f"👤 Récupération profil client: {current_customer.email} [Request-ID: {x_request_id}]")
    return current_customer

@router.put("/me", response_model=schemas.CustomerResponse)
def update_current_customer_profile(
    customer_update: schemas.CustomerUpdate,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """✏️ Mettre à jour le profil du client authentifié"""
    logger.info(f"✏️ Mise à jour profil: {current_customer.email} [Request-ID: {x_request_id}]")
    
    # Vérifier si l'email est déjà utilisé par un autre client
    if customer_update.email and customer_update.email != current_customer.email:
        existing_customer = CustomerService.get_customer_by_email(db, customer_update.email)
        if existing_customer:
            logger.warning(f"❌ Email déjà utilisé: {customer_update.email} [Request-ID: {x_request_id}]")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Email already taken",
                    "message": "Cette adresse email est déjà utilisée",
                    "service": "customers-api"
                }
            )
    
    updated_customer = CustomerService.update_customer(db, current_customer.id, customer_update)
    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Customer not found",
                "message": "Client non trouvé",
                "service": "customers-api"
            }
        )
    
    logger.info(f"✅ Profil mis à jour: {updated_customer.email} [Request-ID: {x_request_id}]")
    return schemas.CustomerResponse.from_orm(updated_customer)

@router.post("/me/change-password")
def change_customer_password(
    password_data: schemas.PasswordChange,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔑 Changer le mot de passe du client"""
    logger.info(f"🔑 Changement de mot de passe: {current_customer.email} [Request-ID: {x_request_id}]")
    
    success = CustomerService.change_password(db, current_customer.id, password_data)
    if not success:
        logger.warning(f"❌ Échec changement mot de passe: {current_customer.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Password change failed",
                "message": "Mot de passe actuel incorrect",
                "service": "customers-api"
            }
        )
    
    logger.info(f"✅ Mot de passe changé: {current_customer.email} [Request-ID: {x_request_id}]")
    return {"message": "Mot de passe mis à jour avec succès"}

@router.delete("/me")
def deactivate_current_customer(
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🗑️ Désactiver le compte du client authentifié"""
    logger.info(f"🗑️ Désactivation compte: {current_customer.email} [Request-ID: {x_request_id}]")
    
    success = CustomerService.deactivate_customer(db, current_customer.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Customer not found",
                "message": "Client non trouvé",
                "service": "customers-api"
            }
        )
    
    logger.info(f"✅ Compte désactivé: {current_customer.email} [Request-ID: {x_request_id}]")
    return {"message": "Compte désactivé avec succès"}

# Endpoints administratifs
@router.get("/", response_model=List[schemas.CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📋 Lister les clients (administratif)"""
    logger.info(f"📋 Récupération liste clients (skip={skip}, limit={limit}) [Request-ID: {x_request_id}]")
    
    customers = CustomerService.get_customers(db, skip=skip, limit=limit, active_only=active_only)
    return [schemas.CustomerResponse.from_orm(customer) for customer in customers]

@router.get("/stats", response_model=schemas.CustomerStats)
def get_customer_statistics(
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📊 Statistiques des clients"""
    logger.info(f"📊 Récupération statistiques clients [Request-ID: {x_request_id}]")
    
    stats = StatsService.get_customer_stats(db)
    return stats

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Obtenir un client par ID (administratif)"""
    logger.info(f"🔍 Récupération client ID: {customer_id} [Request-ID: {x_request_id}]")
    
    customer = CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Customer not found",
                "message": "Client non trouvé",
                "service": "customers-api"
            }
        )
    
    return schemas.CustomerResponse.from_orm(customer) 