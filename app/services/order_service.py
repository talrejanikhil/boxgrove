from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import ItemStatus, Order, OrderItem, OrderStatus, Return, utcnow

RETURN_WINDOW_DAYS = 30
DELIVERY_LAG_DAYS = 5
DELIVERY_ESTIMATE_DAYS = (4, 7)


class ReturnError(Exception):
    pass


@dataclass
class Shipment:
    order_id: int
    status: OrderStatus
    estimated_delivery_from: date | None = None
    estimated_delivery_to: date | None = None


def get_order(session: Session, order_id: int) -> Order | None:
    return session.get(Order, order_id)


def track_shipment(session: Session, order_id: int) -> Shipment | None:
    order = get_order(session, order_id)
    if order is None:
        return None
    shipment = Shipment(order.id, order.status)
    if order.status in (OrderStatus.PROCESSING, OrderStatus.SHIPPED):
        low, high = DELIVERY_ESTIMATE_DAYS
        shipment.estimated_delivery_from = (order.created_at + timedelta(days=low)).date()
        shipment.estimated_delivery_to = (order.created_at + timedelta(days=high)).date()
    return shipment


def initiate_return(session: Session, order_item_id: int, reason: str, now: datetime | None = None) -> Return:
    item = session.get(OrderItem, order_item_id)
    if item is None:
        raise ReturnError(f"Order item {order_item_id} not found")
    if not reason.strip():
        raise ReturnError("A reason is required")
    if item.status is not ItemStatus.ACTIVE:
        raise ReturnError(f"Order item {order_item_id} already has a return ({item.status})")
    if item.order.status is not OrderStatus.DELIVERED:
        raise ReturnError(f"Order {item.order_id} is {item.order.status}, only delivered orders can be returned")
    deadline = item.order.created_at + timedelta(days=DELIVERY_LAG_DAYS + RETURN_WINDOW_DAYS)
    if (now or utcnow()) > deadline:
        raise ReturnError(f"The {RETURN_WINDOW_DAYS}-day return window for order {item.order_id} has closed")

    item.status = ItemStatus.RETURN_REQUESTED
    ret = Return(order_item=item, reason=reason.strip())
    session.add(ret)
    session.commit()
    return ret
