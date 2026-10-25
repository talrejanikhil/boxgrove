import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import (
    Category,
    Customer,
    ItemStatus,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    Return,
    ReturnStatus,
)


def make_order(session: Session) -> OrderItem:
    category = Category(name="home")
    product = Product(category=category, name="Lamp", description="A lamp", price=20.0, sku="HOME-1")
    customer = Customer(name="Ada", email="ada@example.com")
    order = Order(customer=customer, total=40.0)
    item = OrderItem(order=order, product=product, qty=2, unit_price=20.0)
    session.add_all([category, product, customer, order, item])
    session.commit()
    return item


def test_defaults_and_relationships(session: Session) -> None:
    item = make_order(session)
    assert item.order.status is OrderStatus.PROCESSING
    assert item.status is ItemStatus.ACTIVE
    assert item.order.customer.orders == [item.order]
    assert item.product.category.products == [item.product]
    assert item.order.created_at is not None


def test_return_links_to_item(session: Session) -> None:
    item = make_order(session)
    session.add(Return(order_item=item, reason="broken"))
    session.commit()
    assert item.returns[0].status is ReturnStatus.REQUESTED


def test_unique_sku(session: Session) -> None:
    item = make_order(session)
    session.add(Product(category_id=item.product.category_id, name="X", description="x", price=1.0, sku="HOME-1"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_settings_defaults() -> None:
    assert Settings(_env_file=None).qdrant_url == "http://localhost:6333"
