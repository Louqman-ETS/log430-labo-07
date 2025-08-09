import os
import json
import logging
import threading
import time
from typing import Optional

import redis
from fastapi import FastAPI
from pydantic import BaseModel


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Event Notifier")


@app.on_event("startup")
def on_startup():
    start_consumer_thread()


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


def send_notification(event: dict):
    # Minimal placeholder: log notification (could integrate with email provider)
    logger.info(
        f"Notification => type={event.get('event_type')} aggregate={event.get('aggregate_type')}:{event.get('aggregate_id')}"
    )


def consume_forever():
    redis_url = os.getenv("EVENT_BUS_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
    stream = os.getenv("EVENT_STREAM", "ecommerce.carts.events")
    group = os.getenv("EVENT_GROUP", "notifier-consumers")
    consumer_name = os.getenv("CONSUMER_NAME", f"notifier-{os.getpid()}")
    block_ms = int(os.getenv("XREAD_BLOCK_MS", "5000"))

    client = redis.from_url(redis_url, decode_responses=True)

    # Ensure stream and group exist
    try:
        client.xgroup_create(stream, group, id="$", mkstream=True)
    except redis.ResponseError:
        pass

    logger.info(f"Notifier consumer started: stream={stream} group={group} name={consumer_name}")

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

                        # Apply idempotency by deduplicating on message_id using a short-lived Redis SET
                        dedup_key = f"notifier:dedup:{message_id}"
                        if client.setnx(dedup_key, 1):
                            client.expire(dedup_key, 3600)
                            send_notification(event)
                        client.xack(stream, group, message_id)
                    except Exception as e:
                        logger.exception(f"Error processing message {message_id}: {e}")
        except Exception as e:
            logger.exception(f"Consumer loop error: {e}")
            time.sleep(2)


def start_consumer_thread():
    t = threading.Thread(target=consume_forever, daemon=True)
    t.start()


