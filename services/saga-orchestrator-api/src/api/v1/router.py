from fastapi import APIRouter
from .sagas import router as sagas_router

api_router = APIRouter()

# Inclure le routeur des sagas
api_router.include_router(sagas_router, prefix="/sagas", tags=["sagas"]) 