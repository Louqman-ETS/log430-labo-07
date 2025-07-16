from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from src.database import Base


class SagaState(PyEnum):
    """États possibles d'une saga"""
    PENDING = "pending"
    STOCK_CHECKING = "stock_checking"
    STOCK_RESERVED = "stock_reserved"
    ORDER_CREATED = "order_created"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_COMPLETED = "payment_completed"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep(PyEnum):
    """Étapes possibles d'une saga"""
    CHECK_STOCK = "check_stock"
    RESERVE_STOCK = "reserve_stock"
    CREATE_ORDER = "create_order"
    PROCESS_PAYMENT = "process_payment"
    CONFIRM_ORDER = "confirm_order"
    
    # Étapes de compensation
    RELEASE_STOCK = "release_stock"
    CANCEL_ORDER = "cancel_order"
    REFUND_PAYMENT = "refund_payment"


class SagaStepStatus(PyEnum):
    """Statut d'une étape de saga"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


class Saga(Base):
    """Modèle principal d'une saga"""
    __tablename__ = "sagas"

    id = Column(Integer, primary_key=True, index=True)
    saga_id = Column(String, unique=True, index=True, nullable=False)
    saga_type = Column(String, nullable=False)  # "order_processing"
    state = Column(Enum(SagaState), default=SagaState.PENDING)
    
    # Données de la saga
    payload = Column(JSON)  # Données initiales de la transaction
    result = Column(JSON)   # Résultat final
    error_message = Column(Text)
    
    # Méta-données
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    
    # Relations
    steps = relationship("SagaStepExecution", back_populates="saga", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Saga(id={self.saga_id}, type={self.saga_type}, state={self.state.value})>"


class SagaStepExecution(Base):
    """Modèle d'exécution d'une étape de saga"""
    __tablename__ = "saga_step_executions"

    id = Column(Integer, primary_key=True, index=True)
    saga_id = Column(String, ForeignKey("sagas.saga_id"), index=True, nullable=False)
    step = Column(Enum(SagaStep), nullable=False)
    step_order = Column(Integer, nullable=False)  # Ordre d'exécution
    status = Column(Enum(SagaStepStatus), default=SagaStepStatus.PENDING)
    
    # Données de l'étape
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Durée d'exécution
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)  # Durée en millisecondes
    
    # Informations de compensation
    compensation_step = Column(Enum(SagaStep))
    compensation_data = Column(JSON)
    
    # Relation
    saga = relationship("Saga", back_populates="steps")
    
    def __repr__(self):
        return f"<SagaStepExecution(saga_id={self.saga_id}, step={self.step.value}, status={self.status.value})>"


class SagaEvent(Base):
    """Modèle d'événements de saga pour l'audit et le monitoring"""
    __tablename__ = "saga_events"

    id = Column(Integer, primary_key=True, index=True)
    saga_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)  # "state_changed", "step_started", "step_completed", etc.
    event_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SagaEvent(saga_id={self.saga_id}, type={event_type})>" 