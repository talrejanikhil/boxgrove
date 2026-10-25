from langchain_core.tools import tool

from app.db import session as db
from app.db.models import Product
from app.services import catalog_service


def product_payload(p: Product) -> dict:
    return {
        "product_id": p.id,
        "sku": p.sku,
        "name": p.name,
        "category": p.category.name,
        "description": p.description,
        "price": p.price,
        "currency": p.currency,
        "in_stock": p.stock_qty > 0,
    }


@tool(parse_docstring=True)
def get_product_details(product_id: int | None = None, query: str | None = None) -> dict:
    """Look up catalog products by exact id, or search by keywords. Provide product_id or query.

    Args:
        product_id: Exact product id, when known.
        query: Free-text keywords such as a product name or feature, when the id is unknown.
    """
    with db.get_session() as session:
        if product_id is not None:
            product = catalog_service.get_product(session, product_id)
            return {"products": [product_payload(product)] if product else []}
        if query:
            return {"products": [product_payload(p) for p in catalog_service.search_products(session, query)]}
    return {"error": "Provide product_id or query"}


@tool(parse_docstring=True)
def check_inventory(product_id: int) -> dict:
    """Check how many units of a product are in stock.

    Args:
        product_id: Product id.
    """
    with db.get_session() as session:
        product = catalog_service.get_product(session, product_id)
        if product is None:
            return {"error": f"Product {product_id} not found"}
        return {"product_id": product.id, "name": product.name, "stock_qty": product.stock_qty}


@tool(parse_docstring=True)
def recommend_products(category: str | None = None, based_on_product_id: int | None = None) -> dict:
    """Recommend in-stock products, either from a category or similar to a given product.

    Args:
        category: Category name such as Apparel, Electronics, Home, Outdoors, Beauty, Kids or Pets.
        based_on_product_id: Product id to find similar products for. Takes precedence over category.
    """
    if category is None and based_on_product_id is None:
        return {"error": "Provide category or based_on_product_id"}
    with db.get_session() as session:
        products = catalog_service.recommend_products(session, category, based_on_product_id)
        return {"products": [product_payload(p) for p in products]}
