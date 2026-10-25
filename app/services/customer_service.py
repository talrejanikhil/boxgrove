from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Customer, Order


def get_customer(session: Session, customer_id: int) -> Customer | None:
    return session.get(Customer, customer_id)


def get_customer_orders(session: Session, customer_id: int) -> list[Order]:
    query = select(Order).where(Order.customer_id == customer_id).order_by(Order.created_at.desc())
    return list(session.scalars(query))
