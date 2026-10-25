from datetime import datetime, timedelta

import pytest
from langchain_core.tools import BaseTool
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ItemStatus, Order, OrderStatus, Product
from app.services import order_service
from app.tools import catalog_tools, order_tools, retrieval_tools, return_tools

NOW = datetime(2026, 10, 25)

ALL = [
    catalog_tools.get_product_details,
    catalog_tools.check_inventory,
    catalog_tools.recommend_products,
    order_tools.get_order_status,
    order_tools.track_shipment,
    order_tools.get_customer_orders,
    return_tools.initiate_return,
    retrieval_tools.search_knowledge_base,
]


@pytest.mark.parametrize("t", ALL, ids=lambda t: t.name)
def test_tool_has_description_and_arg_docs(t: BaseTool) -> None:
    assert t.description
    assert all(a.get("description") for a in t.args.values())


def test_product_lookup(tool_db: Session) -> None:
    by_query = catalog_tools.get_product_details.invoke({"query": "rain jacket"})
    assert by_query["products"][0]["name"] == "Waterproof Rain Jacket"
    pid = by_query["products"][0]["product_id"]
    assert catalog_tools.get_product_details.invoke({"product_id": pid})["products"][0]["product_id"] == pid
    assert "error" in catalog_tools.get_product_details.invoke({})


def test_inventory_and_recommendations(tool_db: Session) -> None:
    oos = tool_db.scalars(select(Product).where(Product.sku == "ELE-010")).one()
    assert catalog_tools.check_inventory.invoke({"product_id": oos.id})["stock_qty"] == 0
    assert "error" in catalog_tools.check_inventory.invoke({"product_id": 9999})
    recs = catalog_tools.recommend_products.invoke({"category": "Pets"})["products"]
    assert recs
    assert all(p["category"] == "Pets" and p["in_stock"] for p in recs)
    assert "error" in catalog_tools.recommend_products.invoke({})


def test_order_tools(tool_db: Session) -> None:
    order = tool_db.scalars(select(Order).where(Order.status == OrderStatus.SHIPPED)).first()
    status = order_tools.get_order_status.invoke({"order_id": order.id})
    assert status["status"] == "shipped"
    assert status["items"][0]["order_item_id"]
    assert order_tools.track_shipment.invoke({"order_id": order.id})["estimated_delivery_to"]
    orders = order_tools.get_customer_orders.invoke({"customer_id": order.customer_id})["orders"]
    assert order.id in [o["order_id"] for o in orders]
    assert "error" in order_tools.get_order_status.invoke({"order_id": 1})
    assert "error" in order_tools.get_customer_orders.invoke({"customer_id": 9999})


def test_initiate_return_tool_writes_and_reports_errors(tool_db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(order_service, "utcnow", lambda: NOW)
    processing = tool_db.scalars(select(Order).where(Order.status == OrderStatus.PROCESSING)).first()
    assert "error" in return_tools.initiate_return.invoke({"order_item_id": processing.items[0].id, "reason": "x"})

    delivered = tool_db.scalars(
        select(Order).where(Order.status == OrderStatus.DELIVERED, Order.created_at > NOW - timedelta(days=30))
    )
    item = next(i for o in delivered for i in o.items if i.status is ItemStatus.ACTIVE)
    result = return_tools.initiate_return.invoke({"order_item_id": item.id, "reason": "Wrong size"})
    assert result["status"] == "requested"
    tool_db.refresh(item)
    assert item.status is ItemStatus.RETURN_REQUESTED
