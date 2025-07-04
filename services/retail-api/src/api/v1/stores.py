from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.models as models
import src.schemas as schemas
from src.services import StoreService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.StoreResponse])
async def get_stores(
    actif: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """Récupérer la liste des magasins"""
    logger.info(f"🏪 Getting stores - actif={actif}")

    service = StoreService(db)
    return service.get_stores(actif=actif)


@router.post("/", response_model=schemas.StoreResponse, status_code=201)
async def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    """Créer un nouveau magasin"""
    logger.info(f"➕ Creating store: {store.nom}")

    service = StoreService(db)
    return service.create_store(store)


@router.get("/{store_id}", response_model=schemas.StoreResponse)
async def get_store(store_id: int, db: Session = Depends(get_db)):
    """Récupérer un magasin par son ID"""
    logger.info(f"🏪 Getting store {store_id}")

    service = StoreService(db)
    store = service.get_store(store_id)

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return store


@router.put("/{store_id}", response_model=schemas.StoreResponse)
async def update_store(
    store_id: int, store_update: schemas.StoreUpdate, db: Session = Depends(get_db)
):
    """Mettre à jour un magasin"""
    logger.info(f"✏️ Updating store {store_id}")

    service = StoreService(db)
    store = service.update_store(store_id, store_update)

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return store


@router.delete("/{store_id}", status_code=204)
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    """Supprimer un magasin (désactivation logique)"""
    logger.info(f"🗑️ Deleting store {store_id}")

    service = StoreService(db)
    success = service.delete_store(store_id)

    if not success:
        raise HTTPException(status_code=404, detail="Store not found")


@router.get("/{store_id}/details", response_model=schemas.StoreWithDetails)
async def get_store_details(store_id: int, db: Session = Depends(get_db)):
    """Obtenir les détails complets d'un magasin avec ses caisses et statistiques"""
    logger.info(f"🏪 Getting store details {store_id}")

    service = StoreService(db)
    store_details = service.get_store_details(store_id)

    if not store_details:
        raise HTTPException(status_code=404, detail="Store not found")

    return store_details


@router.get("/{store_id}/performance", response_model=schemas.StorePerformance)
async def get_store_performance(store_id: int, db: Session = Depends(get_db)):
    """Obtenir les performances d'un magasin"""
    logger.info(f"📊 Getting store performance {store_id}")

    service = StoreService(db)
    performance = service.get_store_performance(store_id)

    if not performance:
        raise HTTPException(status_code=404, detail="Store not found")

    return performance
