from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .replay import rebuild_cart_state


router = APIRouter()


def get_db_session() -> Session:
    db_url = os.getenv("EVENT_STORE_URL", os.getenv("DATABASE_URL", "postgresql://postgres:password@event-store-db:5432/event_store"))
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal()


@router.get("/read-models/carts/{cart_id}")
def read_model_cart(cart_id: str, session: Session = Depends(get_db_session)):
    try:
        state = rebuild_cart_state(session, cart_id)
        if not state.get("customer_id") and not state.get("session_id") and not state.get("items"):
            raise HTTPException(status_code=404, detail="Cart not found in event store")
        return state
    finally:
        session.close()


