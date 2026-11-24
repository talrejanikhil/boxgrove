"""Run the first 5 traffic_test messages with LANGSMITH_TRACING=false, then =true, and compare.

Usage: uv run python scripts/compare_tracing.py
Each run is a fresh subprocess because langsmith reads LANGSMITH_TRACING once per process.
"""

import json
import os
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
from traffic_test import CASES  # noqa: E402

N = 5
MARK = "@@RESULT@@"


def child() -> None:
    from app.agent import orchestrator
    from app.agent.schemas import AgentResult, ChatRequest

    captured: list[AgentResult] = []
    real = orchestrator.run_main_agent

    def spy(req):  # type: ignore[no-untyped-def]
        captured.append(real(req))
        return captured[-1]

    orchestrator.run_main_agent = spy
    out = []
    for _, customer_id, message, _ in CASES[:N]:
        captured.clear()
        req = ChatRequest(session_id=str(uuid.uuid4()), message=message, customer_id=customer_id)
        start = time.perf_counter()
        resp = orchestrator.handle_chat(req)
        seconds = time.perf_counter() - start
        last = captured[-1].response if captured else None
        out.append(
            {
                "intents": sorted(str(i) for i in resp.intents),
                "blocked": resp.blocked,
                "needs_human": last.needs_human if last else None,
                "resolved": sorted(f"{o.intent}={o.resolved}" for o in last.outcomes) if last else [],
                "tools": sorted({t.name for r in captured for t in r.tool_calls}),
                "seconds": seconds,
            }
        )
    print(MARK + json.dumps(out))


def run(tracing: bool) -> list[dict]:
    env = {**os.environ, "LANGSMITH_TRACING": str(tracing).lower()}
    proc = subprocess.run([sys.executable, __file__, "--child"], env=env, capture_output=True, text=True)
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)]
    if proc.returncode or not lines:
        sys.exit(f"tracing={tracing} run failed (exit {proc.returncode}). stderr tail:\n{proc.stderr[-1500:]}")
    return json.loads(lines[-1][len(MARK) :])


def same(a: dict, b: dict) -> bool:
    keys = ("intents", "blocked", "needs_human", "resolved", "tools")
    return all(a[k] == b[k] for k in keys)


def main() -> None:
    off, on = run(False), run(True)
    print(f"{'message':44} {'match':6} {'off(s)':>7} {'on(s)':>7}")
    mismatches = 0
    for (_, _, msg, _), a, b in zip(CASES[:N], off, on, strict=True):
        ok = same(a, b)
        mismatches += not ok
        print(f"{msg[:42]:44} {'YES' if ok else 'NO':6} {a['seconds']:7.2f} {b['seconds']:7.2f}")
        if not ok:
            for k in ("intents", "blocked", "needs_human", "resolved", "tools"):
                if a[k] != b[k]:
                    print(f"    {k}: off={a[k]} on={b[k]}")
    t_off, t_on = sum(r["seconds"] for r in off), sum(r["seconds"] for r in on)
    print(f"\n{N - mismatches}/{N} match. total off={t_off:.1f}s on={t_on:.1f}s")
    sys.exit(1 if mismatches else 0)


if __name__ == "__main__":
    child() if "--child" in sys.argv else main()
