import math
import re
import zlib
from collections.abc import Iterator

import pytest
from qdrant_client import QdrantClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.clients import qdrant
from app.db import session as db
from app.db.models import Base
from app.db.seed import load_fixtures
from app.retrieval import embeddings
from app.retrieval.indexer import index_all


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def seeded(session: Session) -> Session:
    load_fixtures(session)
    return session


@pytest.fixture
def tool_db(seeded: Session, monkeypatch: pytest.MonkeyPatch) -> Session:
    monkeypatch.setattr(db, "SessionLocal", sessionmaker(seeded.get_bind(), expire_on_commit=False))
    return seeded


def fake_embed(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        v = [0.0] * 256
        for word in re.findall(r"[a-z]+", text.lower()):
            v[zlib.crc32(word.encode()) % 256] += 1
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        vectors.append([x / norm for x in v])
    return vectors


@pytest.fixture
def indexed(seeded: Session, monkeypatch: pytest.MonkeyPatch) -> QdrantClient:
    client = QdrantClient(":memory:")
    index_all(seeded, client, fake_embed)
    monkeypatch.setattr(qdrant, "get_qdrant", lambda: client)
    monkeypatch.setattr(embeddings, "embed", fake_embed)
    return client
