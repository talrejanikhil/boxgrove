from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Category, Customer, ItemStatus, Order, OrderItem, Product, Return, ReturnStatus
from app.db.seed import load_fixtures


def count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model))


def test_load_is_idempotent(session: Session) -> None:
    assert load_fixtures(session) is True
    counts = [count(session, m) for m in (Category, Product, Customer, Order, OrderItem, Return)]
    assert load_fixtures(session) is False
    assert counts == [count(session, m) for m in (Category, Product, Customer, Order, OrderItem, Return)]
    assert counts[:4] == [7, 70, 16, 36]


def test_returns_match_item_state(session: Session) -> None:
    load_fixtures(session)
    returns = session.scalars(select(Return)).all()
    assert returns
    for r in returns:
        expected = ItemStatus.RETURNED if r.status is ReturnStatus.REFUNDED else ItemStatus.RETURN_REQUESTED
        assert r.order_item.status is expected


def test_order_totals_match_items(session: Session) -> None:
    load_fixtures(session)
    for order in session.scalars(select(Order)):
        assert round(sum(i.qty * i.unit_price for i in order.items), 2) == order.total
