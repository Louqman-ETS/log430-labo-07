from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.v1 import crud
from src.api.v1.models import GlobalSummary, StorePerformance, TopProduct
from src.api.v1 import dependencies
from src.db import get_db

router = APIRouter(dependencies=[Depends(dependencies.api_token_auth)])


@router.get("/global-summary", response_model=GlobalSummary)
def read_global_summary(db: Session = Depends(get_db)) -> Any:
    """
    Get a global summary of all sales.
    """
    return crud.get_global_summary(db)


@router.get("/performance-by-store", response_model=List[StorePerformance])
def read_performance_by_store(db: Session = Depends(get_db)) -> Any:
    """
    Get a breakdown of performance for each store.
    """
    return crud.get_performance_by_store(db)


@router.get("/top-selling-products", response_model=List[TopProduct])
def read_top_selling_products(
    db: Session = Depends(get_db),
    store_id: Optional[int] = None,
) -> Any:
    """
    Get the top 15 selling products, optionally filtered by store.
    """
    return crud.get_top_selling_products(db, store_id=store_id)
