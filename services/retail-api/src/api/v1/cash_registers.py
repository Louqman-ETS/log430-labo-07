from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.models as models
import src.schemas as schemas
from src.services import CashRegisterService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.CashRegisterResponse])
async def get_cash_registers(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    actif: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des caisses enregistreuses"""
    logger.info(f"💰 Getting cash registers - store_id={store_id}, actif={actif}")

    service = CashRegisterService(db)
    return service.get_cash_registers(store_id=store_id, actif=actif)


@router.post("/", response_model=schemas.CashRegisterResponse, status_code=201)
async def create_cash_register(
    cash_register: schemas.CashRegisterCreate, db: Session = Depends(get_db)
):
    """Créer une nouvelle caisse enregistreuse"""
    logger.info(f"➕ Creating cash register: {cash_register.nom}")

    service = CashRegisterService(db)
    return service.create_cash_register(cash_register)


@router.get("/{cash_register_id}", response_model=schemas.CashRegisterResponse)
async def get_cash_register(cash_register_id: int, db: Session = Depends(get_db)):
    """Récupérer une caisse enregistreuse par son ID"""
    logger.info(f"💰 Getting cash register {cash_register_id}")

    service = CashRegisterService(db)
    cash_register = service.get_cash_register(cash_register_id)

    if not cash_register:
        raise HTTPException(status_code=404, detail="Cash register not found")

    return cash_register


@router.put("/{cash_register_id}", response_model=schemas.CashRegisterResponse)
async def update_cash_register(
    cash_register_id: int,
    cash_register_update: schemas.CashRegisterUpdate,
    db: Session = Depends(get_db),
):
    """Mettre à jour une caisse enregistreuse"""
    logger.info(f"✏️ Updating cash register {cash_register_id}")

    service = CashRegisterService(db)
    cash_register = service.update_cash_register(cash_register_id, cash_register_update)

    if not cash_register:
        raise HTTPException(status_code=404, detail="Cash register not found")

    return cash_register


@router.delete("/{cash_register_id}", status_code=204)
async def delete_cash_register(cash_register_id: int, db: Session = Depends(get_db)):
    """Supprimer une caisse enregistreuse (désactivation logique)"""
    logger.info(f"🗑️ Deleting cash register {cash_register_id}")

    service = CashRegisterService(db)
    success = service.delete_cash_register(cash_register_id)

    if not success:
        raise HTTPException(status_code=404, detail="Cash register not found")
