from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import time
import uuid

from src.database import get_db
import src.schemas as schemas
import src.models as models
from src.services import CustomerService, AddressService, AuthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["customers"])


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    """Dependency to get customer service"""
    return CustomerService(db)


def get_address_service(db: Session = Depends(get_db)) -> AddressService:
    return AddressService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================


@router.get("/", response_model=List[schemas.CustomerResponse])
def get_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(
        None, description="Search term for customer name or email"
    ),
    active_only: bool = Query(True, description="Return only active customers"),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des clients avec pagination et recherche"""
    logger.info(
        f"📋 Getting customers - skip={skip}, limit={limit}, search={search}, active_only={active_only}"
    )

    service = CustomerService(db)
    customers = service.get_customers(
        skip=skip, limit=limit, search=search, active_only=active_only
    )

    return customers


@router.get("/{customer_id}", response_model=schemas.CustomerWithAddresses)
def get_customer(
    customer_id: int, service: CustomerService = Depends(get_customer_service)
):
    """Récupérer un client par son ID avec ses adresses"""
    logger.info(f"👤 Getting customer {customer_id}")

    customer = service.get_customer_with_addresses(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    return customer


@router.post(
    "/", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED
)
def create_customer(
    customer: schemas.CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
):
    """Créer un nouveau client"""
    logger.info(f"➕ Creating customer: {customer.email}")

    try:
        created_customer = service.create_customer(customer)
        logger.info(f"✅ Customer created: {created_customer.id}")
        return created_customer
    except ValueError as e:
        logger.error(f"❌ Error creating customer: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int,
    customer_update: schemas.CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
):
    """Mettre à jour un client"""
    logger.info(f"✏️ Updating customer {customer_id}")

    updated_customer = service.update_customer(customer_id, customer_update)
    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    logger.info(f"✅ Customer updated: {customer_id}")
    return updated_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int, service: CustomerService = Depends(get_customer_service)
):
    """Supprimer un client (désactivation logique)"""
    logger.info(f"🗑️ Deleting customer {customer_id}")

    success = service.delete_customer(customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    logger.info(f"✅ Customer deleted: {customer_id}")


@router.get(
    "/{customer_id}/with-addresses", response_model=schemas.CustomerWithAddresses
)
def get_customer_with_addresses(
    customer_id: int, service: CustomerService = Depends(get_customer_service)
):
    """Récupérer un client avec ses adresses"""
    customer = service.get_customer_with_addresses(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/stats/summary", response_model=schemas.CustomerStats)
def get_customer_statistics(service: CustomerService = Depends(get_customer_service)):
    """Récupérer les statistiques des clients"""
    return service.get_customer_stats()


# ============================================================================
# ADDRESS ENDPOINTS
# ============================================================================


@router.get("/{customer_id}/addresses", response_model=List[schemas.AddressResponse])
def get_customer_addresses(
    customer_id: int,
    address_type: Optional[schemas.AddressType] = Query(
        None, description="Filter by address type"
    ),
    service: CustomerService = Depends(get_customer_service),
):
    """Récupérer les adresses d'un client"""
    logger.info(f"📍 Getting addresses for customer {customer_id}")

    addresses = service.get_customer_addresses(customer_id, address_type)
    return addresses


@router.post(
    "/{customer_id}/addresses",
    response_model=schemas.AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_address(
    customer_id: int,
    address: schemas.AddressCreate,
    service: CustomerService = Depends(get_customer_service),
):
    """Ajouter une adresse à un client"""
    logger.info(f"➕ Adding address for customer {customer_id}")

    try:
        created_address = service.create_customer_address(customer_id, address)
        logger.info(f"✅ Address created: {created_address.id}")
        return created_address
    except ValueError as e:
        logger.error(f"❌ Error creating address: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{customer_id}/addresses/{address_id}", response_model=schemas.AddressResponse
)
def update_customer_address(
    customer_id: int,
    address_id: int,
    address_update: schemas.AddressUpdate,
    service: CustomerService = Depends(get_customer_service),
):
    """Mettre à jour une adresse d'un client"""
    logger.info(f"✏️ Updating address {address_id} for customer {customer_id}")

    updated_address = service.update_customer_address(
        customer_id, address_id, address_update
    )
    if not updated_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    logger.info(f"✅ Address updated: {address_id}")
    return updated_address


@router.delete(
    "/{customer_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_customer_address(
    customer_id: int,
    address_id: int,
    service: CustomerService = Depends(get_customer_service),
):
    """Supprimer une adresse d'un client"""
    logger.info(f"🗑️ Deleting address {address_id} for customer {customer_id}")

    success = service.delete_customer_address(customer_id, address_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    logger.info(f"✅ Address deleted: {address_id}")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    login_data: schemas.CustomerLogin,
    service: CustomerService = Depends(get_customer_service),
):
    """Authentifier un client"""
    logger.info(f"🔐 Customer login attempt: {login_data.email}")

    try:
        result = service.authenticate_customer(login_data.email, login_data.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        customer, token = result
        logger.info(f"✅ Customer logged in: {customer.id}")
        return schemas.LoginResponse(customer=customer, token=token)
    except ValueError as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/register",
    response_model=schemas.LoginResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    registration: schemas.CustomerRegister,
    service: CustomerService = Depends(get_customer_service),
):
    """Enregistrer un nouveau client"""
    logger.info(f"📝 Customer registration: {registration.email}")

    try:
        result = service.register_customer(registration)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed"
            )

        customer, token = result
        logger.info(f"✅ Customer registered: {customer.id}")
        return schemas.LoginResponse(customer=customer, token=token)
    except ValueError as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{customer_id}/change-password", status_code=status.HTTP_200_OK)
def change_password(
    customer_id: int,
    password_change: schemas.PasswordChange,
    service: CustomerService = Depends(get_customer_service),
):
    """Changer le mot de passe d'un client"""
    logger.info(f"🔒 Password change for customer {customer_id}")

    try:
        success = service.change_password(
            customer_id, password_change.current_password, password_change.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed"
            )

        logger.info(f"✅ Password changed for customer {customer_id}")
        return {"message": "Password changed successfully"}
    except ValueError as e:
        logger.error(f"❌ Password change error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================


@router.get("/stats/overview", response_model=schemas.CustomerStats)
def get_customer_stats(service: CustomerService = Depends(get_customer_service)):
    """Obtenir les statistiques des clients"""
    logger.info("📊 Getting customer statistics")

    stats = service.get_customer_stats()
    return stats
