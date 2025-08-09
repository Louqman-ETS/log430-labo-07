import os
import json
import logging
import threading
import time
from typing import List, Dict

import redis
import httpx
from fastapi import FastAPI


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ORDERS_STREAM = os.getenv("ORDERS_EVENT_STREAM", "ecommerce.orders.events")
PAYMENTS_STREAM = os.getenv("PAYMENTS_EVENT_STREAM", "ecommerce.payments.events")
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL", "redis://redis:6379/0")
INVENTORY_API = os.getenv("INVENTORY_API_URL", "http://inventory-api:8001")
GROUP = os.getenv("EVENT_GROUP", "inventory-saga")


def publish(client: redis.Redis, stream: str, event: Dict) -> None:
    try:
        client.xadd(stream, {"event": json.dumps(event)})
    except Exception as e:
        logger.warning(f"Failed to publish to {stream}: {e}")


async def reserve_items(items: List[Dict]) -> bool:
    async with httpx.AsyncClient() as client:
        for it in items:
            product_id = it.get("product_id")
            qty = it.get("quantity", 0)
            resp = await client.put(
                f"{INVENTORY_API}/api/v1/stock/products/{product_id}/stock/reduce",
                params={"quantity": qty, "raison": "order_reservation", "reference": f"order_{int(time.time())}"},
            )
            if resp.status_code != 200:
                return False
    return True


async def compensate_items(items: List[Dict]) -> None:
    async with httpx.AsyncClient() as client:
        for it in items:
            product_id = it.get("product_id")
            qty = it.get("quantity", 0)
            await client.put(
                f"{INVENTORY_API}/api/v1/stock/products/{product_id}/stock/increase",
                params={"quantity": qty, "raison": "order_compensation", "reference": f"comp_{int(time.time())}"},
            )


def consume_forever():
    client = redis.from_url(EVENT_BUS_URL, decode_responses=True)

    for stream in (ORDERS_STREAM, PAYMENTS_STREAM):
        try:
            client.xgroup_create(stream, GROUP, id="$", mkstream=True)
        except redis.ResponseError:
            pass

    logger.info(f"Inventory saga consumer started on streams: {ORDERS_STREAM}, {PAYMENTS_STREAM}")

    while True:
        try:
            resp = client.xreadgroup(GROUP, os.getenv("CONSUMER_NAME", "inv-saga-1"),
                                     {ORDERS_STREAM: ">", PAYMENTS_STREAM: ">"}, count=20, block=5000)
            if not resp:
                continue
            for stream, messages in resp:
                for message_id, fields in messages:
                    try:
                        event_json = fields.get("event")
                        if not event_json:
                            client.xack(stream, GROUP, message_id)
                            continue
                        event = json.loads(event_json)
                        etype = event.get("event_type")
                        data = event.get("data", {})
                        order_id = event.get("aggregate_id")

                        if stream == ORDERS_STREAM and etype == "OrderCreated":
                            # Try to reserve stock
                            import asyncio
                            ok = asyncio.run(reserve_items(data.get("items", [])))
                            out = {
                                "event_id": f"stock-{int(time.time()*1000)}",
                                "event_type": "StockReserved" if ok else "StockReservationFailed",
                                "stream": ORDERS_STREAM,
                                "occurred_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "aggregate_type": "Order",
                                "aggregate_id": order_id,
                                "data": {"ok": ok},
                            }
                            publish(client, ORDERS_STREAM, out)

                        elif stream == PAYMENTS_STREAM and etype == "PaymentFailed":
                            import asyncio
                            asyncio.run(compensate_items(data.get("items", [])))
                            out = {
                                "event_id": f"comp-{int(time.time()*1000)}",
                                "event_type": "StockCompensated",
                                "stream": PAYMENTS_STREAM,
                                "occurred_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "aggregate_type": "Order",
                                "aggregate_id": order_id,
                                "data": {},
                            }
                            publish(client, PAYMENTS_STREAM, out)

                        client.xack(stream, GROUP, message_id)
                    except Exception as e:
                        logger.exception(f"Error processing {stream}@{message_id}: {e}")
        except Exception as e:
            logger.exception(f"Consumer loop error: {e}")
            time.sleep(2)


app = FastAPI(title="Inventory Saga Consumer")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    t = threading.Thread(target=consume_forever, daemon=True)
    t.start()


