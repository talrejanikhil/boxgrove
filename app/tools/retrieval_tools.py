from langchain_core.tools import tool

from app.retrieval import qdrant_client


@tool(parse_docstring=True)
def search_knowledge_base(query: str) -> dict:
    """Search product descriptions and store policies (shipping, returns, warranty, payment methods).

    Use for policy questions and for product details or comparisons not covered by the catalog tools.
    Answer only from the returned text.

    Args:
        query: A natural-language question or keywords.
    """
    docs = qdrant_client.retrieve(query)
    return {
        "results": [
            {"doc_type": d["metadata"]["doc_type"], "title": d["metadata"]["title"],
             "text": d["page_content"], "score": d["metadata"]["score"]}
            for d in docs
        ],
    }
