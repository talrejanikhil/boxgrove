from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

_env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR), undefined=StrictUndefined, keep_trailing_newline=True, autoescape=True
)


def render_prompt(name: str, **variables: object) -> str:
    return _env.get_template(name).render(**variables)
