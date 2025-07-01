from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ...database import get_db
from ...services import AddressService
from ... import schemas
from .customers import get_current_customer

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.AddressResponse])
def get_customer_addresses(
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """📍 Obtenir toutes les adresses du client authentifié"""
    logger.info(f"📍 Récupération adresses client: {current_customer.email} [Request-ID: {x_request_id}]")
    
    addresses = AddressService.get_customer_addresses(db, current_customer.id)
    return [schemas.AddressResponse.from_orm(address) for address in addresses]

@router.post("/", response_model=schemas.AddressResponse, status_code=status.HTTP_201_CREATED)
def create_customer_address(
    address_data: schemas.AddressCreate,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🏠 Créer une nouvelle adresse pour le client"""
    logger.info(f"🏠 Création adresse {address_data.type.value} pour: {current_customer.email} [Request-ID: {x_request_id}]")
    
    try:
        address = AddressService.create_address(db, current_customer.id, address_data)
        logger.info(f"✅ Adresse créée (ID: {address.id}) pour {current_customer.email} [Request-ID: {x_request_id}]")
        return schemas.AddressResponse.from_orm(address)
        
    except Exception as e:
        logger.error(f"❌ Erreur création adresse: {str(e)} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Address creation failed",
                "message": "Erreur lors de la création de l'adresse",
                "service": "customers-api"
            }
        )

@router.get("/{address_id}", response_model=schemas.AddressResponse)
def get_customer_address(
    address_id: int,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🔍 Obtenir une adresse spécifique du client"""
    logger.info(f"🔍 Récupération adresse {address_id} pour: {current_customer.email} [Request-ID: {x_request_id}]")
    
    address = AddressService.get_address(db, address_id, current_customer.id)
    if not address:
        logger.warning(f"❌ Adresse {address_id} non trouvée pour: {current_customer.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Address not found",
                "message": "Adresse non trouvée",
                "service": "customers-api"
            }
        )
    
    return schemas.AddressResponse.from_orm(address)

@router.put("/{address_id}", response_model=schemas.AddressResponse)
def update_customer_address(
    address_id: int,
    address_update: schemas.AddressUpdate,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """✏️ Mettre à jour une adresse du client"""
    logger.info(f"✏️ Mise à jour adresse {address_id} pour: {current_customer.email} [Request-ID: {x_request_id}]")
    
    updated_address = AddressService.update_address(db, address_id, current_customer.id, address_update)
    if not updated_address:
        logger.warning(f"❌ Adresse {address_id} non trouvée pour mise à jour: {current_customer.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Address not found",
                "message": "Adresse non trouvée",
                "service": "customers-api"
            }
        )
    
    logger.info(f"✅ Adresse {address_id} mise à jour pour: {current_customer.email} [Request-ID: {x_request_id}]")
    return schemas.AddressResponse.from_orm(updated_address)

@router.delete("/{address_id}")
def delete_customer_address(
    address_id: int,
    current_customer: schemas.CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db),
    x_request_id: Optional[str] = Header(None)
):
    """🗑️ Supprimer une adresse du client"""
    logger.info(f"🗑️ Suppression adresse {address_id} pour: {current_customer.email} [Request-ID: {x_request_id}]")
    
    success = AddressService.delete_address(db, address_id, current_customer.id)
    if not success:
        logger.warning(f"❌ Adresse {address_id} non trouvée pour suppression: {current_customer.email} [Request-ID: {x_request_id}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Address not found",
                "message": "Adresse non trouvée",
                "service": "customers-api"
            }
        )
    
    logger.info(f"✅ Adresse {address_id} supprimée pour: {current_customer.email} [Request-ID: {x_request_id}]")
    return {"message": "Adresse supprimée avec succès"} 