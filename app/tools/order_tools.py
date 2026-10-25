from langchain_core.tools import tool

from app.db import session as db
from app.db.models import Order
from app.services import customer_service, order_service


def order_payload(order: Order) -> dict:
    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "order_item_id": i.id,
                "product_id": i.product_id,
                "product_name": i.product.name,
                "qty": i.qty,
                "unit_price": i.unit_price,
                "status": i.status,
            }
            for i in order.items
        ],
    }


@tool(parse_docstring=True)
def get_order_status(order_id: int) -> dict:
    """Get an order's status, total and line items, including each order_item_id needed to start a return.

    Args:
        order_id: Order id.
    """
    with db.get_session() as session:
        order = order_service.get_order(session, order_id)
        return order_payload(order) if order else {"error": f"Order {order_id} not found"}


@tool(parse_docstring=True)
def track_shipment(order_id: int) -> dict:
    """Get shipment progress and the estimated delivery window for an order.

    Args:
        order_id: Order id.
    """
    with db.get_session() as session:
        shipment = order_service.track_shipment(session, order_id)
        if shipment is None:
            return {"error": f"Order {order_id} not found"}
        return {
            "order_id": shipment.order_id,
            "status": shipment.status,
            "estimated_delivery_from": shipment.estimated_delivery_from
            and shipment.estimated_delivery_from.isoformat(),
            "estimated_delivery_to": shipment.estimated_delivery_to and shipment.estimated_delivery_to.isoformat(),
        }


@tool(parse_docstring=True)
def get_customer_orders(customer_id: int) -> dict:
    """List a customer's orders, newest first.

    Args:
        customer_id: Customer id.
    """
    with db.get_session() as session:
        if customer_service.get_customer(session, customer_id) is None:
            return {"error": f"Customer {customer_id} not found"}
        return {"orders": [order_payload(o) for o in customer_service.get_customer_orders(session, customer_id)]}
