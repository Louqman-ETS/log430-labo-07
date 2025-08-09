import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Optional

import redis
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, StoredEvent


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class HealthResponse(BaseModel):
    status: str


def get_db_url() -> str:
    return os.getenv("EVENT_STORE_URL", os.getenv("DATABASE_URL", "postgresql://postgres:password@event-store-db:5432/event_store"))


def get_redis_url() -> str:
    return os.getenv("EVENT_BUS_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))


DB_ENGINE = create_engine(get_db_url())
SessionLocal = sessionmaker(bind=DB_ENGINE, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=DB_ENGINE)


app = FastAPI(title="Event Audit API")


@app.on_event("startup")
def on_startup():
    init_db()
    start_consumer_thread()
    # Include HTTP API for queries/replay
    try:
        from .api import router as api_router
        app.include_router(api_router, prefix="/api/v1")
    except Exception as e:
        logger.warning(f"Failed to include API router: {e}")


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/events/{aggregate_type}/{aggregate_id}")
def get_events(aggregate_type: str, aggregate_id: str):
    session = SessionLocal()
    try:
        events = (
            session.query(StoredEvent)
            .filter(
                StoredEvent.aggregate_type == aggregate_type,
                StoredEvent.aggregate_id == aggregate_id,
            )
            .order_by(StoredEvent.occurred_at.asc())
            .all()
        )
        return [
            {
                "id": ev.id,
                "event_id": ev.event_id,
                "event_type": ev.event_type,
                "stream": ev.stream,
                "occurred_at": ev.occurred_at.isoformat(),
                "payload": json.loads(ev.payload),
            }
            for ev in events
        ]
    finally:
        session.close()


def consume_forever():
    redis_url = get_redis_url()
    stream = os.getenv("EVENT_STREAM", "ecommerce.carts.events")
    group = os.getenv("EVENT_GROUP", "audit-consumers")
    consumer_name = os.getenv("CONSUMER_NAME", f"audit-{os.getpid()}")
    block_ms = int(os.getenv("XREAD_BLOCK_MS", "5000"))

    client = redis.from_url(redis_url, decode_responses=True)

    # Ensure stream and group exist
    try:
        client.xgroup_create(stream, group, id="$", mkstream=True)
    except redis.ResponseError:
        # Group exists
        pass

    logger.info(f"Audit consumer started: stream={stream} group={group} name={consumer_name}")

    while True:
        try:
            resp = client.xreadgroup(group, consumer_name, {stream: ">"}, count=50, block=block_ms)
            if not resp:
                continue
            for _, messages in resp:
                for message_id, fields in messages:
                    try:
                        event_json = fields.get("event")
                        if not event_json:
                            client.xack(stream, group, message_id)
                            continue
                        event = json.loads(event_json)
                        # Structured log (JSON)
                        logger.info(json.dumps({"received_event": event}, ensure_ascii=False))

                        # Store in DB (Event Store) with idempotency on message_id
                        session = SessionLocal()
                        try:
                            exists = (
                                session.query(StoredEvent)
                                .filter(StoredEvent.message_id == message_id)
                                .first()
                            )
                            if not exists:
                                stored = StoredEvent(
                                    message_id=message_id,
                                    event_id=event.get("event_id"),
                                    event_type=event.get("event_type"),
                                    stream=event.get("stream"),
                                    aggregate_type=event.get("aggregate_type"),
                                    aggregate_id=str(event.get("aggregate_id")),
                                    occurred_at=datetime.fromisoformat(event.get("occurred_at")),
                                    payload=json.dumps(event, ensure_ascii=False),
                                )
                                session.add(stored)
                                session.commit()
                        finally:
                            session.close()

                        client.xack(stream, group, message_id)
                    except Exception as e:
                        logger.exception(f"Error processing message {message_id}: {e}")
                        # Don't ack to allow retry
        except Exception as e:
            logger.exception(f"Consumer loop error: {e}")
            time.sleep(2)


def start_consumer_thread():
    t = threading.Thread(target=consume_forever, daemon=True)
    t.start()


