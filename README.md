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

## LangSmith setup

Edit `.env` only; never commit it. Do not set `LANGSMITH_PROJECT`.

1. Create an account and API key: [Create an account and API key](https://docs.langchain.com/langsmith/create-account-api-key).
2. Create an agent and copy its ID: [Create an agent](https://docs.langchain.com/langsmith/create-an-agent).
3. Set `LANGSMITH_API_KEY` to your key and `LANGSMITH_TRACING` to `true`.
4. Set `LANGSMITH_AGENT_ID` to the agent ID.
5. Set `LANGSMITH_AGENT_ENVIRONMENT` to `local`.
6. If your account is not on the US site, set `LANGSMITH_ENDPOINT` to your region's API URL. The key must come from the same region.
   - US: `https://api.smith.langchain.com` (default)
   - EU: `https://eu.api.smith.langchain.com`
   - APAC: `https://apac.api.smith.langchain.com`
   - AWS US: `https://aws.api.smith.langchain.com`
7. Check the setup and send a test trace:
   ```bash
   uv run python scripts/check_setup.py --send-trace
   ```
8. In LangSmith, open your agent's `local` environment and look for a run named `check_langsmith`.

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
