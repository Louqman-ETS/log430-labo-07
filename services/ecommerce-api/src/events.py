import os
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import redis


logger = logging.getLogger(__name__)


class EventPublisher:
    """Simple Redis Streams publisher for domain events.

    Events are serialized as JSON and appended to a Redis Stream.
    Each event includes:
      - event_id (UUID)
      - event_type (str)
      - stream (str)
      - occurred_at (ISO-8601 UTC)
      - aggregate_type (str)
      - aggregate_id (str|int)
      - data (dict)
    """

    def __init__(self):
        redis_url = os.getenv("EVENT_BUS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.stream_name = os.getenv("EVENT_STREAM", "ecommerce.carts.events")
        self.instance_id = os.getenv("INSTANCE_ID", "ecommerce-api")
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Quick ping to validate connection; if it fails we will work in degraded mode
            self.client.ping()
            self.enabled = True
            logger.info(f"EventPublisher connected to Redis at {redis_url}, stream='{self.stream_name}'")
        except Exception as e:
            self.client = None
            self.enabled = False
            logger.warning(f"EventPublisher disabled (Redis unavailable): {e}")

    def publish(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: Any,
        data: Optional[Dict[str, Any]] = None,
        stream: Optional[str] = None,
    ) -> Optional[str]:
        if not self.enabled or not self.client:
            return None

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "stream": stream or self.stream_name,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "aggregate_type": aggregate_type,
            "aggregate_id": str(aggregate_id),
            "producer_instance": self.instance_id,
            "data": data or {},
        }

        try:
            message_id = self.client.xadd(event["stream"], {"event": json.dumps(event)})
            logger.info(
                f"Published event to {event['stream']}: type={event_type} aggregate={aggregate_type}:{aggregate_id} id={event['event_id']} msg_id={message_id}"
            )
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish event '{event_type}': {e}")
            return None


