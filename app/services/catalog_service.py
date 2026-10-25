from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Category, Product


def get_product(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)


def search_products(session: Session, query: str, limit: int = 5) -> list[Product]:
    terms = [t for t in query.lower().split() if len(t) > 2]
    if not terms:
        return []
    matches = session.scalars(
        select(Product).where(
            or_(*(c.ilike(f"%{t}%") for t in terms for c in (Product.name, Product.description, Product.sku)))
        )
    ).all()

    def score(p: Product) -> int:
        return sum((2 if t in p.name.lower() else 0) + (t in p.description.lower()) for t in terms)

    return sorted(matches, key=lambda p: (-score(p), p.id))[:limit]


def check_inventory(session: Session, product_id: int) -> int | None:
    product = get_product(session, product_id)
    return product.stock_qty if product else None


def recommend_products(
    session: Session, category: str | None = None, based_on_product_id: int | None = None, limit: int = 5
) -> list[Product]:
    in_stock = Product.stock_qty > 0
    if based_on_product_id is not None:
        base = get_product(session, based_on_product_id)
        if base is None:
            return []
        query = (
            select(Product)
            .where(Product.category_id == base.category_id, Product.id != base.id, in_stock)
            .order_by(func.abs(Product.price - base.price), Product.id)
        )
    elif category:
        query = (
            select(Product)
            .join(Category)
            .where(func.lower(Category.name) == category.lower(), in_stock)
            .order_by(Product.price, Product.id)
        )
    else:
        raise ValueError("category or based_on_product_id is required")
    return list(session.scalars(query.limit(limit)))
