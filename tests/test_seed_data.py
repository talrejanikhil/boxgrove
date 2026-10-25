import json
from pathlib import Path

SEED = Path(__file__).parent.parent / "data" / "seed"
DOCS = Path(__file__).parent.parent / "data" / "docs"


def load(name: str) -> list:
    return json.loads((SEED / f"{name}.json").read_text())


def test_counts() -> None:
    assert 6 <= len(load("categories")) <= 8
    assert 60 <= len(load("products")) <= 80
    assert 15 <= len(load("customers")) <= 20
    assert 30 <= len(load("orders")) <= 40
    assert len(list(DOCS.glob("*.md"))) >= 4


def test_references_and_totals() -> None:
    categories = set(load("categories"))
    products = {p["sku"]: p for p in load("products")}
    emails = {c["email"] for c in load("customers")}
    assert len(products) == len(load("products"))
    assert all(p["category"] in categories for p in products.values())
    for order in load("orders"):
        assert order["customer_email"] in emails
        assert all(i["sku"] in products for i in order["items"])
        assert order["total"] == round(sum(i["qty"] * i["unit_price"] for i in order["items"]), 2)


def test_order_state_coverage() -> None:
    orders = load("orders")
    assert {o["status"] for o in orders} == {"processing", "shipped", "delivered", "returned"}
    returned = [i for o in orders if o["status"] == "returned" for i in o["items"]]
    assert returned
    assert all(i["status"] == "returned" and "return" in i for i in returned)
