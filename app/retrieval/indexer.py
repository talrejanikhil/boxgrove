import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients import qdrant
from app.config import settings
from app.db.models import Product
from app.retrieval import embeddings, qdrant_client

DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "docs"


@dataclass
class Document:
    key: str
    text: str
    payload: dict


def policy_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    documents = []
    for path in sorted(docs_dir.glob("*.md")):
        title, *sections = re.split(r"^## ", path.read_text(), flags=re.M)
        doc_title = title.removeprefix("# ").strip()
        for section in sections:
            heading = section.splitlines()[0].strip()
            documents.append(
                Document(
                    key=f"policy:{path.stem}:{heading}",
                    text=f"{doc_title} - {heading}\n\n{section.strip()}",
                    payload={"doc_type": "policy", "title": f"{doc_title} - {heading}", "source": path.name},
                )
            )
    return documents


def specs_text(p: Product) -> str:
    specs = {
        "Colors": ", ".join(p.colors),
        "Sizes": ", ".join(p.sizes),
        "Dimensions": p.dimensions,
        "Weight": p.weight,
        "Material": p.material,
    }
    return "".join(f" {k}: {v}." for k, v in specs.items() if v)


def product_documents(session: Session) -> list[Document]:
    return [
        Document(
            key=f"product:{p.id}",
            text=f"{p.name} ({p.category.name}). {p.description}{specs_text(p)}",
            payload={
                "doc_type": "product",
                "title": p.name,
                "product_id": p.id,
                "sku": p.sku,
                "category": p.category.name,
                "price": p.price,
            },
        )
        for p in session.scalars(select(Product).order_by(Product.id))
    ]


def index_all(
    session: Session,
    client: QdrantClient | None = None,
    embed: Callable[[list[str]], list[list[float]]] = embeddings.embed,
) -> int:
    client = client or qdrant.get_qdrant()
    documents = [*product_documents(session), *policy_documents()]
    collection = settings.qdrant_collection
    # ponytail: skips on matching count only; delete the collection to re-index after editing content
    if client.collection_exists(collection) and client.count(collection).count == len(documents):
        return 0

    vectors = embed([d.text for d in documents])
    qdrant_client.ensure_collection(client, len(vectors[0]))
    client.upsert(
        collection,
        points=[
            PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, d.key)), vector=v, payload={**d.payload, "text": d.text})
            for d, v in zip(documents, vectors, strict=True)
        ],
    )
    return len(documents)
