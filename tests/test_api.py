import pytest
from fastapi.testclient import TestClient
from openai import OpenAIError
from sqlalchemy.orm import Session

from app.agent.schemas import ChatRequest, ChatResponse, Intent
from app.api import routes
from app.main import app

client = TestClient(app)


def test_chat_returns_orchestrator_response(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[ChatRequest] = []

    def fake(request: ChatRequest) -> ChatResponse:
        seen.append(request)
        return ChatResponse(session_id=request.session_id, reply="Hi!", intents=[Intent.SMALL_TALK])

    monkeypatch.setattr(routes, "handle_chat", fake)
    response = client.post("/chat", json={"session_id": "s1", "message": "Hello", "customer_id": 3})
    assert response.status_code == 200
    assert response.json() == {"session_id": "s1", "reply": "Hi!", "intents": ["small_talk"], "blocked": False}
    assert seen[0].customer_id == 3


@pytest.mark.parametrize(
    "body", [{"session_id": "s", "message": ""}, {"message": "hi"}, {"session_id": "s", "message": "x" * 2001}]
)
def test_chat_rejects_invalid_requests(body: dict) -> None:
    assert client.post("/chat", json=body).status_code == 422


def test_chat_maps_openai_errors_to_502(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(request: ChatRequest) -> ChatResponse:
        raise OpenAIError("down")

    monkeypatch.setattr(routes, "handle_chat", boom)
    response = client.post("/chat", json={"session_id": "s", "message": "hi"})
    assert response.status_code == 502
    assert "temporarily unavailable" in response.json()["detail"]


def test_customers_lists_seeded_customers(tool_db: Session) -> None:
    customers = client.get("/customers").json()
    assert len(customers) == 16
    assert set(customers[0]) == {"id", "name"}


def test_index_and_static_assets_are_served() -> None:
    index = client.get("/")
    assert index.status_code == 200
    assert "Boxgrove Support" in index.text
    assert client.get("/static/chat.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
