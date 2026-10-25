import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Category, Customer, ItemStatus, Order, OrderItem, OrderStatus, Product, Return, ReturnStatus
from app.db.session import SessionLocal, init_db

SEED_DIR = Path(__file__).resolve().parents[2] / "data" / "seed"


def read(name: str) -> list:
    return json.loads((SEED_DIR / f"{name}.json").read_text())


def load_fixtures(session: Session) -> bool:
    if session.scalar(select(Category.id).limit(1)) is not None:
        return False

    categories = {name: Category(name=name) for name in read("categories")}
    products = {
        p["sku"]: Product(
            category=categories[p["category"]],
            name=p["name"],
            description=p["description"],
            price=p["price"],
            currency=p["currency"],
            stock_qty=p["stock_qty"],
            sku=p["sku"],
        )
        for p in read("products")
    }
    customers = {c["email"]: Customer(**c) for c in read("customers")}

    orders = []
    for o in read("orders"):
        order = Order(
            id=o["id"],
            customer=customers[o["customer_email"]],
            status=OrderStatus(o["status"]),
            total=o["total"],
            created_at=datetime.fromisoformat(o["created_at"]),
        )
        for i in o["items"]:
            item = OrderItem(
                order=order,
                product=products[i["sku"]],
                qty=i["qty"],
                unit_price=i["unit_price"],
                status=ItemStatus(i["status"]),
            )
            if r := i.get("return"):
                item.returns.append(
                    Return(
                        status=ReturnStatus(r["status"]),
                        reason=r["reason"],
                        created_at=datetime.fromisoformat(r["created_at"]),
                    )
                )
        orders.append(order)

    session.add_all([*categories.values(), *products.values(), *customers.values(), *orders])
    session.commit()
    return True


def main() -> None:
    init_db()
    with SessionLocal() as session:
        print("Seeded database" if load_fixtures(session) else "Database already seeded")


if __name__ == "__main__":
    main()
