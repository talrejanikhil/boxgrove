# Boxgrove

Multicategory e-commerce chat agent. Running example for the book *Prompting LangSmith for LLMOps*.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Docker
- OpenAI API key

## Setup

```bash
uv sync
cp .env.example .env   # set OPENAI_API_KEY
docker compose up -d   # Qdrant
uv run python -m app.db.seed
```

Seeding is skipped once data exists. After editing `data/seed/` or the schema, reseed from scratch:

```bash
rm boxgrove.db
curl -X DELETE localhost:6333/collections/boxgrove
uv run python -m app.db.seed
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000.

## Test

```bash
uv run pytest
```

## Branches

One branch per chapter, each building on the previous: `main` → `chapter_1` … `chapter_8`. Each is the answer key for
its chapter.
