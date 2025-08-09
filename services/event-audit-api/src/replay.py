from typing import Dict, Any, List
from sqlalchemy.orm import Session

from .models import StoredEvent


def rebuild_cart_state(session: Session, cart_id: str) -> Dict[str, Any]:
    """Simple replay function for Cart aggregate.

    Applies CartCreated, CartItemAdded events to produce a read model.
    """
    events: List[StoredEvent] = (
        session.query(StoredEvent)
        .filter(StoredEvent.aggregate_type == "Cart", StoredEvent.aggregate_id == str(cart_id))
        .order_by(StoredEvent.occurred_at.asc())
        .all()
    )

    state: Dict[str, Any] = {
        "cart_id": str(cart_id),
        "customer_id": None,
        "session_id": None,
        "items": [],
        "total_items": 0,
        "total_amount": 0.0,
    }

    for ev in events:
        payload = ev.payload
        # payload is JSON string
        import json

        event = json.loads(payload)
        etype = event.get("event_type")
        data = event.get("data", {})

        if etype == "CartCreated":
            state["customer_id"] = data.get("customer_id")
            state["session_id"] = data.get("session_id")
        elif etype == "CartItemAdded":
            item = {
                "cart_item_id": data.get("cart_item_id"),
                "product_id": data.get("product_id"),
                "quantity": data.get("quantity", 0),
                "unit_price": float(data.get("unit_price", 0)),
            }
            state["items"].append(item)
            state["total_items"] += item["quantity"]
            state["total_amount"] += item["quantity"] * item["unit_price"]
        elif etype == "CartCheckedOut":
            state["checked_out"] = True
            state["order_id"] = data.get("order_id")

    return state


