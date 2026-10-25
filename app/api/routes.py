from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAIError
from sqlalchemy import select

from app.agent.orchestrator import handle_chat
from app.agent.schemas import ChatRequest, ChatResponse
from app.db import session as db
from app.db.models import Customer

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter()


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/customers")
def customers() -> list[dict]:
    with db.get_session() as session:
        return [{"id": c.id, "name": c.name} for c in session.scalars(select(Customer).order_by(Customer.name))]


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return handle_chat(request)
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail="The assistant is temporarily unavailable") from e
