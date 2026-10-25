# AGENTS.md

## Architecture

Per-turn flow in `app/agent/orchestrator.py`:

1. Input guardrail (regex) — blocks abuse, injection, off-domain
2. Intent Classifier (OpenAI Decisions API) — multi-label intents
3. Main Agent (OpenAI Responses API) — tool-calling loop per intent
4. Output guardrail (regex) — blocks invented discounts, PII leaks
5. Response

Session history lives in `app/agent/memory.py`.

## Layout

- `app/agent/` — orchestrator, classifier, main agent, guardrails, memory, schemas
- `app/tools/` — LangChain `@tool` wrappers, agent-facing
- `app/services/` — business logic and SQLAlchemy queries
- `app/retrieval/` — Qdrant search, embeddings, indexer
- `app/clients/` — cached OpenAI and Qdrant clients
- `app/db/` — models, session, seeding
- `app/api/` — FastAPI routes and static chat UI
- `prompts/` — Markdown prompts
- `data/seed/` — fixtures; `data/docs/` — policy docs indexed into Qdrant

## Rules

- Tools stay thin: no business logic, call into `services/`. Tool docstrings are the model-facing description.
- Every Intent Classifier and Main Agent call takes and returns a Pydantic model from `app/agent/schemas.py`. No raw
  dicts or free-text parsing.
- Prompts live in `prompts/` as Markdown with `{{variable}}` placeholders (Jinja2). No inline prompt strings.
- Get OpenAI and Qdrant clients from `app/clients/`; do not construct your own.
- Config via `app/config.py` (`.env`).
- Minimal comments, type hints everywhere. Lint with `uv run ruff check`.
- No observability or tracing code in `main`.

## Commands

```bash
uv sync
docker compose up -d
uv run python -m app.db.seed
uv run uvicorn app.main:app --reload
uv run pytest
```
