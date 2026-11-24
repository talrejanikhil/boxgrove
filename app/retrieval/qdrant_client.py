from langsmith import traceable
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

from app.clients import qdrant
from app.config import settings
from app.retrieval import embeddings


def ensure_collection(client: QdrantClient, size: int) -> None:
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            settings.qdrant_collection, vectors_config=VectorParams(size=size, distance=Distance.COSINE)
        )


def search(client: QdrantClient, vector: list[float], limit: int = 4, doc_type: str | None = None) -> list[dict]:
    query_filter = Filter(must=[FieldCondition(key="doc_type", match=MatchValue(value=doc_type))]) if doc_type else None
    response = client.query_points(
        settings.qdrant_collection, query=vector, query_filter=query_filter, limit=limit, with_payload=True
    )
    return [{**(point.payload or {}), "score": round(point.score, 4)} for point in response.points]


@traceable(name="qdrant_search", run_type="retriever")
def retrieve(query: str, limit: int = 4, doc_type: str | None = None) -> list[dict]:
    vector = embeddings.embed([query])[0]
    results = search(qdrant.get_qdrant(), vector, limit, doc_type)
    return [
        {
            "page_content": r["text"],
            "type": "Document",
            "metadata": {k: r.get(k) for k in ("source", "doc_type", "title", "score")},
        }
        for r in results
    ]
