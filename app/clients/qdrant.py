from functools import lru_cache

from qdrant_client import QdrantClient

from app.config import settings


@lru_cache
def get_qdrant() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)
