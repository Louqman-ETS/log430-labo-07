from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from ...services import CategoryService

router = APIRouter()

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    category_service: CategoryService = Depends(get_category_service),
):
    """Retrieve all categories."""
    return category_service.get_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    """Get category by ID."""
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    return category

@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
):
    """Create new category."""
    try:
        return category_service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
):
    """Update a category completely."""
    try:
        updated_category = category_service.update_category(category_id, category)
        if not updated_category:
            raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
        return updated_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    """Delete a category."""
    # First get the category to return it
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")

    # Then delete it
    try:
        deleted = category_service.delete_category(category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 