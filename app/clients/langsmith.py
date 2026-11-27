import langsmith
from langsmith import Client
from langsmith.anonymizer import create_anonymizer

from app.agent.guardrails import mask_pii


def setup_tracing() -> None:
    """Mask PII in every run (inputs, outputs, error, metadata), incl. wrap_openai runs, before upload."""
    langsmith.configure(client=Client(anonymizer=create_anonymizer(mask_pii, max_depth=20)))
