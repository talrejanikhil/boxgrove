# Troubleshooting a missing or rejected LangSmith trace

Work top to bottom. Each step is more expensive than the one before, so stop at the first one that explains the failure.

Sources: [Create an account and API key](https://docs.langchain.com/langsmith/create-account-api-key), [Log traces to an agent](https://docs.langchain.com/langsmith/log-traces-to-agent), [Trace with LangChain](https://docs.langchain.com/langsmith/trace-with-langchain).

Fastest smoke test for the whole setup: `uv run python scripts/check_langsmith.py`. It prints which variables are set (
never their values), sends one `check_langsmith` run, and flushes.

## Free: read the environment (seconds)

1. **All four variables are set.** `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_AGENT_ID`,
   `LANGSMITH_AGENT_ENVIRONMENT`. The SDK needs the agent ID and environment *together*; one alone names no destination
   and nothing is traced.
2. **Environment is one of** `local`, `development`, `staging`, `production` (not case-sensitive). There is no default.
3. **No legacy destination variable is set.** If `LANGSMITH_PROJECT`, `LANGCHAIN_PROJECT`, or `LANGCHAIN_SESSION` is set
   next to the agent variables, the SDK logs a warning at client start and silently skips tracing. Unset them.
4. **`.env` is actually loaded and the shell isn't overriding it.** Print `os.getenv("LANGSMITH_TRACING")` at the top of
   the entry point. A stale exported variable or a `.env` loaded after the SDK client is created gives wrong values (
   see [variable caching](https://docs.langchain.com/langsmith/troubleshooting-variable-caching)).
5. **SDK version.** `langsmith>=0.14.9` is required to send traces to an agent. Check with `uv pip show langsmith`.

## Cheap: read the error code (a minute)

6. **401 — "I don't know who you are."** LangSmith did not recognize the API key.
   **Check one thing:** the key matches the region. EU, APAC, and AWS accounts must set `LANGSMITH_ENDPOINT` (e.g.
   `https://eu.api.smith.langchain.com`); against the default US endpoint a valid key is "not recognized". Second
   suspect: the key was deleted, or a PAT was deactivated.
7. **403 — "I know who you are, you can't do that here."** The key is valid but not allowed.
   **Check one thing:** the key's scope. It must belong to the workspace that owns the agent, and a tracing key only has
   `runs:create` and `projects:create`. If the app also reads traces, use a PAT or service key instead. Also: on
   self-hosted LangSmith, runs sent to an agent get `403 agent addressing is not enabled for this workspace` (agent
   workspaces are Cloud only) and the *whole request* is dropped.
8. **409 — "That destination is taken or unavailable."**
   **Check one thing:** the agent is not archived. An archived agent still holds its identifier, and LangSmith rejects
   runs sent to it with `409`. Unarchive it or use a different agent ID.
9. **"Agent does not exist."** Not a status code you'll always see, but same family: the identifier is wrong or the
   agent was never created in this workspace. Use the **ID** field on the agent's Overview page, not its display name.

## Cheap: no error, no trace (a few minutes)

Tracing failures are quiet by design: the SDK never raises into your app.

10. **Look in the right place.** In LangSmith: select the agent, open **Tracing**, and set the environment control to
    the one you sent to. A trace sent to `local` does not show under `production`.
11. **Check the right workspace.** The key's workspace and the one open in the UI must match.
12. **Tracing really is on for this call.** `LANGSMITH_TRACING` must be set before the traced code runs. Code outside a
    `@traceable` function or LangChain call is never traced; `tracing_context(enabled=False)` or a missing decorator on
    the entry function looks identical to a broken setup.
13. **Turn up logging.** Run with `LANGSMITH_TRACING=true` and Python logging at `DEBUG` for `langsmith`. Upload
    failures that were swallowed show up here, including 4xx bodies.

## Cheap: short script that exits before upload

14. **Flush before exit.** Traces upload in a background thread. A script, test, or serverless handler can end before
    the batch is sent, so the run is lost with no error. Fix:
    - Plain SDK / `@traceable`: call `client.flush()` on the `Client` you passed to the decorator (this is what
      `scripts/check_langsmith.py` does).
    - LangChain: call `wait_for_all_tracers()` from `langchain_core.tracers.langchain` before exit.
      The long-running FastAPI app is usually fine; this bites scripts, seed jobs, pytest runs, and cron.

## Expensive: reproduce outside the app (tens of minutes)

15. **Minimal reproduction.** Run `scripts/check_langsmith.py` with the same `.env`. If it works and the app does not,
    the problem is in app wiring (steps 3, 4, 12, 14). If it fails too, the problem is the key, region, or agent (steps
    6–9).
16. **Raw request.** Call the API directly with the same key to separate "key rejected" from "SDK not sending":
    ```bash
    curl -s -o /dev/null -w "%{http_code}\n" \
      -H "X-Api-Key: $LANGSMITH_API_KEY" \
      "$LANGSMITH_ENDPOINT/api/v1/workspaces"
    ```
    `200` means the key and region are fine. Note this uses a read endpoint, so a tracing-only key will correctly return
    `403` here; that is not a tracing failure.
17. **Rotate the key.** Create a fresh key in **Settings > API Keys**, update `.env`, rerun step 15. Last resort because
    it can break other consumers of the old key.

## Production watch-outs

- Tracing is best-effort and silent. Nothing in the request path tells you traces stopped; alert on "no traces in N
  minutes" in LangSmith rather than relying on app errors.
- Never paste the API key into logs, tickets, or `curl` output while debugging. Report whether a variable is set, not
  its value.
