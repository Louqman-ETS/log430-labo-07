from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...schemas import CashRegisterCreate, CashRegisterUpdate, CashRegisterResponse
from ...services import CashRegisterService

router = APIRouter()

def get_cash_register_service(db: Session = Depends(get_db)) -> CashRegisterService:
    return CashRegisterService(db)

@router.get("/", response_model=List[CashRegisterResponse])
def read_cash_registers(
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Retrieve all cash registers."""
    return cash_register_service.get_all_cash_registers()

@router.get("/{register_id}", response_model=CashRegisterResponse)
def read_cash_register(
    register_id: int,
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Get cash register by ID."""
    register = cash_register_service.get_cash_register(register_id)
    if not register:
        raise HTTPException(status_code=404, detail=f"Cash register with id {register_id} not found")
    return register

@router.get("/store/{store_id}", response_model=List[CashRegisterResponse])
def read_cash_registers_by_store(
    store_id: int,
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Get all cash registers for a specific store."""
    return cash_register_service.get_cash_registers_by_store(store_id)

@router.post("/", response_model=CashRegisterResponse, status_code=201)
def create_cash_register(
    register: CashRegisterCreate,
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Create new cash register."""
    try:
        return cash_register_service.create_cash_register(register)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{register_id}", response_model=CashRegisterResponse)
def update_cash_register(
    register_id: int,
    register: CashRegisterUpdate,
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Update a cash register completely."""
    try:
        updated_register = cash_register_service.update_cash_register(register_id, register)
        if not updated_register:
            raise HTTPException(status_code=404, detail=f"Cash register with id {register_id} not found")
        return updated_register
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{register_id}", response_model=CashRegisterResponse)
def delete_cash_register(
    register_id: int,
    cash_register_service: CashRegisterService = Depends(get_cash_register_service),
):
    """Delete a cash register."""
    # First get the register to return it
    register = cash_register_service.get_cash_register(register_id)
    if not register:
        raise HTTPException(status_code=404, detail=f"Cash register with id {register_id} not found")

    # Then delete it
    deleted = cash_register_service.delete_cash_register(register_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Cash register with id {register_id} not found")

    return register 