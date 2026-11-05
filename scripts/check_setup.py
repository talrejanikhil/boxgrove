import argparse
import os
import re
import subprocess
import sys
import tomllib
import urllib.request
from collections.abc import Callable
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_LANGSMITH = (0, 14, 9)
FORBIDDEN = ["LANGSMITH_PROJECT", "LANGCHAIN_PROJECT", "LANGCHAIN_SESSION"]

Result = str | None  # None = pass, otherwise the next step to take


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def check_python() -> Result:
    spec = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["requires-python"]
    required = version_tuple(spec)
    if sys.version_info[: len(required)] < required:
        return f"Install Python {spec} (`uv python install`) and rerun with `uv run`."
    return None


def check_langsmith_version() -> Result:
    try:
        installed = metadata.version("langsmith")
    except metadata.PackageNotFoundError:
        return "Run `uv sync` to install langsmith."
    if version_tuple(installed) < MIN_LANGSMITH:
        return f"Upgrade langsmith to {'.'.join(map(str, MIN_LANGSMITH))} or later with `uv sync`."
    return None


def check_docker() -> Result:
    try:
        ok = subprocess.run(["docker", "info"], capture_output=True, timeout=15).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        ok = False
    return None if ok else "Install and start Docker Desktop, then rerun."


def check_qdrant() -> Result:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    try:
        urllib.request.urlopen(url, timeout=5).close()
    except OSError:
        return "Run `docker compose up -d` and check QDRANT_URL if you changed it."
    return None


def check_env_vars() -> Result:
    names = re.findall(r"^\s*([A-Za-z_]\w*)\s*=", (ROOT / ".env.example").read_text(), re.M)
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        return f"Set in .env or the shell: {', '.join(missing)}."
    return None


def check_no_project_vars() -> Result:
    found = [n for n in FORBIDDEN if os.getenv(n)]
    if found:
        return f"Unset {', '.join(found)}; the agent id and environment route traces instead."
    return None


def check_trace() -> Result:
    # Subprocess output is dropped: check_langsmith.py prints the agent id and environment values
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_langsmith.py")], capture_output=True, timeout=60, cwd=ROOT
    )
    if proc.returncode != 0:
        return "Run `uv run python scripts/check_langsmith.py` directly to see why the trace failed."
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send-trace", action="store_true", help="also run the check_langsmith.py connectivity check")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    checks: list[tuple[str, Callable[[], Result]]] = [
        ("Python version", check_python),
        ("langsmith >= 0.14.9", check_langsmith_version),
        ("Docker reachable", check_docker),
        ("Qdrant reachable", check_qdrant),
        (".env.example variables set", check_env_vars),
        ("no LANGSMITH_PROJECT/LANGCHAIN_PROJECT/LANGCHAIN_SESSION", check_no_project_vars),
    ]
    if args.send_trace:
        checks.append(("LangSmith trace sent", check_trace))

    failed = 0
    for label, fn in checks:
        try:
            fix = fn()
        except Exception as e:
            fix = f"Check crashed ({type(e).__name__}); inspect scripts/check_setup.py."
        if fix is None:
            print(f"PASS {label}")
        else:
            failed += 1
            print(f"FAIL {label}: {fix}")

    print(f"{len(checks) - failed}/{len(checks)} checks passed" if failed else f"All {len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
