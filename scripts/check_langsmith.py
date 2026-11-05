import os

from dotenv import load_dotenv
from langsmith import Client, traceable

# Load .env so the LANGSMITH_* variables are in the environment
load_dotenv()

# Report whether each required variable is set, never its value
REQUIRED = ["LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_AGENT_ID", "LANGSMITH_AGENT_ENVIRONMENT"]
missing = [n for n in REQUIRED if not os.getenv(n)]
for n in REQUIRED:
    print(f"{n}: {'NOT SET' if n in missing else 'set'}")
if missing:
    raise SystemExit(f"Missing: {', '.join(missing)}")

# One explicit client, shared by the traced function and the final flush
client = Client()


# One traced function; the decorator records it as a run
@traceable(name="check_langsmith", client=client)
def ping() -> str:
    return "pong"


# Run it once
print("result:", ping())

# Traces upload in a background thread, so flush before the process exits
client.flush()

# Point to where the trace should appear
print(
    f"Done. In LangSmith open Agents -> {os.environ['LANGSMITH_AGENT_ID']} -> "
    f"environment '{os.environ['LANGSMITH_AGENT_ENVIRONMENT']}' -> Traces, "
    "and look for the run named 'check_langsmith'."
)
