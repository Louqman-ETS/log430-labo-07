from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import time

from src.database import get_db
from src.saga_orchestrator import SagaOrchestrator
from src.models import Saga, SagaEvent, SagaState
from src.schemas import (
    OrderProcessingSagaRequest,  # Gardé pour usage interne
    CustomerOrderProcessingSagaRequest,
    SagaResponse,
    SagaListResponse,
    SagaStatsResponse,
    SagaEventResponse
)
from src.metrics_service import metrics_service

logger = logging.getLogger(__name__)
router = APIRouter()


def get_orchestrator(db: Session = Depends(get_db)) -> SagaOrchestrator:
    """Factory pour créer l'orchestrateur de saga"""
    return SagaOrchestrator(db)


@router.post("/customers/{customer_id}/order-processing", response_model=dict, status_code=202)
async def start_customer_order_processing_saga(
    customer_id: int,
    request: CustomerOrderProcessingSagaRequest,
    background_tasks: BackgroundTasks,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
):
    """Démarre une saga de traitement de commande pour un client spécifique"""
    try:
        logger.info(f"🚀 Starting order processing saga for customer {customer_id}")
        
        # Convertir en OrderProcessingSagaRequest en ajoutant le customer_id
        full_request = OrderProcessingSagaRequest(
            customer_id=customer_id,
            cart_id=request.cart_id,
            products=request.products,
            shipping_address=request.shipping_address,
            billing_address=request.billing_address,
            payment_method=request.payment_method,
            simulate_failure=request.simulate_failure
        )
        
        # Démarrer la saga
        saga_id = await orchestrator.start_order_processing_saga(full_request)
        
        return {
            "message": f"Order processing saga started for customer {customer_id}",
            "saga_id": saga_id,
            "customer_id": customer_id,
            "status": "accepted"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start saga for customer {customer_id}: {e}")
        metrics_service.record_error("saga_start_failed", f"/customers/{customer_id}/order-processing")
        raise HTTPException(status_code=500, detail=f"Failed to start saga: {str(e)}")


@router.get("/{saga_id}", response_model=SagaResponse)
def get_saga_status(
    saga_id: str,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
):
    """Récupère le statut d'une saga"""
    try:
        saga = orchestrator.get_saga_status(saga_id)
        
        if not saga:
            raise HTTPException(status_code=404, detail=f"Saga {saga_id} not found")
        
        return saga
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get saga status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saga status: {str(e)}")


@router.get("/{saga_id}/events", response_model=List[SagaEventResponse])
def get_saga_events(
    saga_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupère les événements d'une saga"""
    try:
        events = (
            db.query(SagaEvent)
            .filter(SagaEvent.saga_id == saga_id)
            .order_by(SagaEvent.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return events
        
    except Exception as e:
        logger.error(f"❌ Failed to get saga events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saga events: {str(e)}")


@router.get("/", response_model=SagaListResponse)
def get_sagas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    saga_type: Optional[str] = Query(None),
    state: Optional[SagaState] = Query(None),
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
):
    """Récupère la liste des sagas avec pagination et filtres"""
    try:
        db = orchestrator.db
        
        # Construire la requête avec filtres
        query = db.query(Saga)
        
        if saga_type:
            query = query.filter(Saga.saga_type == saga_type)
        
        if state:
            query = query.filter(Saga.state == state)
        
        # Compter le total
        total = query.count()
        
        # Récupérer les résultats paginés
        sagas = query.offset(skip).limit(limit).all()
        
        # Calculer les informations de pagination
        pages = (total + limit - 1) // limit
        current_page = (skip // limit) + 1
        
        return SagaListResponse(
            items=sagas,
            total=total,
            page=current_page,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get sagas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sagas: {str(e)}")


@router.get("/stats/summary", response_model=SagaStatsResponse)
def get_saga_statistics(db: Session = Depends(get_db)):
    """Récupère les statistiques des sagas"""
    try:
        # Compter les sagas par état
        total_sagas = db.query(Saga).count()
        pending_sagas = db.query(Saga).filter(Saga.state == SagaState.PENDING).count()
        completed_sagas = db.query(Saga).filter(Saga.state == SagaState.COMPLETED).count()
        failed_sagas = db.query(Saga).filter(Saga.state == SagaState.FAILED).count()
        compensated_sagas = db.query(Saga).filter(Saga.state == SagaState.COMPENSATED).count()
        
        # Calculer la durée moyenne
        completed_sagas_with_duration = (
            db.query(Saga)
            .filter(
                Saga.state == SagaState.COMPLETED,
                Saga.started_at.isnot(None),
                Saga.completed_at.isnot(None)
            )
            .all()
        )
        
        average_duration_ms = None
        if completed_sagas_with_duration:
            total_duration = sum(
                (saga.completed_at - saga.started_at).total_seconds() * 1000
                for saga in completed_sagas_with_duration
            )
            average_duration_ms = total_duration / len(completed_sagas_with_duration)
        
        # Calculer le taux de succès
        total_finished = completed_sagas + failed_sagas + compensated_sagas
        success_rate = completed_sagas / total_finished if total_finished > 0 else 0.0
        
        # Compter les étapes et compensations
        from src.models import SagaStepExecution, SagaStepStatus
        total_steps_executed = db.query(SagaStepExecution).count()
        total_compensations = (
            db.query(SagaStepExecution)
            .filter(SagaStepExecution.status == SagaStepStatus.COMPENSATED)
            .count()
        )
        
        return SagaStatsResponse(
            total_sagas=total_sagas,
            pending_sagas=pending_sagas,
            completed_sagas=completed_sagas,
            failed_sagas=failed_sagas,
            compensated_sagas=compensated_sagas,
            average_duration_ms=average_duration_ms,
            success_rate=success_rate,
            total_steps_executed=total_steps_executed,
            total_compensations=total_compensations
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get saga statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saga statistics: {str(e)}") 