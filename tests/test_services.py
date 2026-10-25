from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ItemStatus, Order, OrderItem, OrderStatus, Product, Return
from app.services import catalog_service, customer_service, order_service
from app.services.order_service import ReturnError

NOW = datetime(2026, 10, 25)


def product_by_sku(session: Session, sku: str) -> Product:
    return session.scalars(select(Product).where(Product.sku == sku)).one()


def test_search_ranks_name_matches_first(seeded: Session) -> None:
    results = catalog_service.search_products(seeded, "wireless earbuds")
    assert results[0].sku == "ELE-001"
    assert catalog_service.search_products(seeded, "zzzz") == []


def test_inventory(seeded: Session) -> None:
    assert catalog_service.check_inventory(seeded, product_by_sku(seeded, "ELE-010").id) == 0
    assert catalog_service.check_inventory(seeded, 9999) is None


def test_recommendations(seeded: Session) -> None:
    base = product_by_sku(seeded, "ELE-001")
    similar = catalog_service.recommend_products(seeded, based_on_product_id=base.id)
    assert similar
    assert all(p.category_id == base.category_id and p.id != base.id and p.stock_qty > 0 for p in similar)
    assert catalog_service.recommend_products(seeded, category="outdoors")
    assert catalog_service.recommend_products(seeded, category="nope") == []
    with pytest.raises(ValueError):
        catalog_service.recommend_products(seeded)


def test_customer_orders_newest_first(seeded: Session) -> None:
    orders = customer_service.get_customer_orders(seeded, 1)
    assert orders
    assert all(o.customer_id == 1 for o in orders)
    assert [o.created_at for o in orders] == sorted((o.created_at for o in orders), reverse=True)
    assert customer_service.get_customer(seeded, 9999) is None


def test_track_shipment(seeded: Session) -> None:
    shipped = seeded.scalars(select(Order).where(Order.status == OrderStatus.SHIPPED)).first()
    assert order_service.track_shipment(seeded, shipped.id).estimated_delivery_to is not None
    delivered = seeded.scalars(select(Order).where(Order.status == OrderStatus.DELIVERED)).first()
    assert order_service.track_shipment(seeded, delivered.id).estimated_delivery_to is None
    assert order_service.track_shipment(seeded, 1) is None


def first_active_item(session: Session, recent: bool) -> OrderItem:
    orders = session.scalars(select(Order).where(Order.status == OrderStatus.DELIVERED).order_by(Order.created_at))
    chosen = [o for o in orders if all(i.status is ItemStatus.ACTIVE for i in o.items)]
    return (chosen[-1] if recent else chosen[0]).items[0]


def test_initiate_return_mutates_db(seeded: Session) -> None:
    item = first_active_item(seeded, recent=True)
    ret = order_service.initiate_return(seeded, item.id, "Wrong size", now=NOW)
    assert ret.id is not None
    assert item.status is ItemStatus.RETURN_REQUESTED
    assert seeded.scalars(select(Return).where(Return.order_item_id == item.id)).one().reason == "Wrong size"


def test_initiate_return_rejections(seeded: Session) -> None:
    old = first_active_item(seeded, recent=False)
    with pytest.raises(ReturnError, match="window"):
        order_service.initiate_return(seeded, old.id, "Too late", now=NOW)
    with pytest.raises(ReturnError, match="not found"):
        order_service.initiate_return(seeded, 99999, "x", now=NOW)
    with pytest.raises(ReturnError, match="reason"):
        order_service.initiate_return(seeded, old.id, "  ", now=NOW)
    processing = seeded.scalars(select(Order).where(Order.status == OrderStatus.PROCESSING)).first()
    with pytest.raises(ReturnError, match="only delivered"):
        order_service.initiate_return(seeded, processing.items[0].id, "x", now=NOW)
    returned = seeded.scalars(select(OrderItem).where(OrderItem.status == ItemStatus.RETURNED)).first()
    with pytest.raises(ReturnError, match="already"):
        order_service.initiate_return(seeded, returned.id, "x", now=NOW)
