from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.database import get_db
import src.models as models
import src.schemas as schemas
from src.services import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Récupérer toutes les catégories"""
    logger.info("📋 Getting all categories")

    service = CategoryService(db)
    return service.get_categories()


@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
async def create_category(
    category: schemas.CategoryCreate, db: Session = Depends(get_db)
):
    """Créer une nouvelle catégorie"""
    logger.info(f"➕ Creating category: {category.nom}")

    service = CategoryService(db)
    return service.create_category(category)


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Récupérer une catégorie par son ID"""
    logger.info(f"📋 Getting category {category_id}")

    service = CategoryService(db)
    category = service.get_category(category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Mettre à jour une catégorie"""
    logger.info(f"✏️ Updating category {category_id}")

    service = CategoryService(db)
    category = service.update_category(category_id, category_update)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Supprimer une catégorie"""
    logger.info(f"🗑️ Deleting category {category_id}")

    service = CategoryService(db)
    success = service.delete_category(category_id)

    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
