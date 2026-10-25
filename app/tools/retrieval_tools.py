from langchain_core.tools import tool

from app.clients import qdrant
from app.retrieval import embeddings, qdrant_client


@tool(parse_docstring=True)
def search_knowledge_base(query: str) -> dict:
    """Search product descriptions and store policies (shipping, returns, warranty, payment methods).

    Use for policy questions and for product details or comparisons not covered by the catalog tools.
    Answer only from the returned text.

    Args:
        query: A natural-language question or keywords.
    """
    vector = embeddings.embed([query])[0]
    results = qdrant_client.search(qdrant.get_qdrant(), vector)
    return {
        "results": [{k: r[k] for k in ("doc_type", "title", "text", "score")} for r in results],
    }
