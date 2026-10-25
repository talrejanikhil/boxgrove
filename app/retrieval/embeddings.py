from app.clients.openai_client import get_openai
from app.config import settings


def embed(texts: list[str]) -> list[list[float]]:
    response = get_openai().embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in response.data]
