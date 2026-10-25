from qdrant_client import QdrantClient
from sqlalchemy.orm import Session

from app.config import settings
from app.retrieval import qdrant_client
from app.retrieval.indexer import index_all, policy_documents, product_documents
from app.tools.retrieval_tools import search_knowledge_base
from tests.conftest import fake_embed


def search(client: QdrantClient, query: str, **kwargs) -> list[dict]:
    return qdrant_client.search(client, fake_embed([query])[0], **kwargs)


def test_documents_cover_products_and_policy_sections(seeded: Session) -> None:
    products, policies = product_documents(seeded), policy_documents()
    assert len(products) == 70
    assert {p.payload["source"] for p in policies} == {"shipping.md", "returns.md", "warranty.md", "payment_methods.md"}
    assert len({d.key for d in [*products, *policies]}) == len(products) + len(policies)


def test_index_is_idempotent(seeded: Session) -> None:
    client = QdrantClient(":memory:")
    total = index_all(seeded, client, fake_embed)
    assert total > 70
    assert index_all(seeded, client, fake_embed) == 0
    assert client.count(settings.qdrant_collection).count == total


def test_policy_and_product_queries(indexed: QdrantClient) -> None:
    policy = search(indexed, "how many days do I have to return an item for a refund")
    assert any(r["doc_type"] == "policy" and "Returns" in r["title"] for r in policy[:3])
    product = search(indexed, "waterproof rain jacket seam-sealed hood")
    assert product[0]["title"] == "Waterproof Rain Jacket"
    assert all(r["doc_type"] == "product" for r in search(indexed, "return window", doc_type="product"))


def test_search_knowledge_base_tool(indexed: QdrantClient) -> None:
    results = search_knowledge_base.invoke({"query": "free standard shipping minimum order"})["results"]
    assert results
    assert set(results[0]) == {"doc_type", "title", "text", "score"}
    assert any("Shipping" in r["title"] for r in results)
